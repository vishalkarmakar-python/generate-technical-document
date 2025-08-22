"""
Orchestrates the entire code analysis and documentation generation pipeline.

This module contains the `Generate` class, which acts as the main controller,
coordinating all steps from loading source files to generating the final
Markdown report. It relies on dependency injection to receive its components,
making it a flexible and testable orchestrator.
"""

from app.create_document import CreateDocument
from app.document_splitter import Document_Splitter
from app.language_model import Ollama
from app.prompt_generator import PromptGenerator
from app.structured_output import Code_Analysis, Code_Structure, Technical_Specification
from langchain_core.documents.base import Document
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from typing import Callable, Dict, List, Tuple

# from langchain_core.messages.base import BaseMessage


class Generate:
    """
    Manages the end-to-end document generation process via dependency injection.

    This class integrates all components of the application:
    1. `Document_Splitter`: To load and chunk the source code.
    2. `PromptGenerator`: To create tailored prompts for the LLM.
    3. `Ollama`: To interact with the language model.
    4. `CreateDocument`: To assemble the final report.
    """

    def __init__(
        self,
        document_splitter: Document_Splitter,
        prompt_generator: PromptGenerator,
        llm_manager: Ollama,
        document_creator: CreateDocument,
    ) -> None:
        """
        Initializes the Generate instance with its required dependencies.

        Args:
            splitter: An instance of Document_Splitter.
            prompt_generator: An instance of PromptGenerator.
            llm_manager: An instance of Ollama.
            document_creator: An instance of CreateDocument.
        """
        self.document_splitter: Document_Splitter = document_splitter
        self.prompt_generator: PromptGenerator = prompt_generator
        self.llm_manager: Ollama = llm_manager
        self.document_creator: CreateDocument = document_creator

    def run(self, file_path: str, output_file_path: str, model_name: str) -> None:
        """
        Executes the full document generation pipeline.

        Args:
            file_path: The directory containing the ABAP source code files.
            output_file_path: The directory where the final Markdown report
                              will be saved.
            model_name: The name of the Ollama model to use for analysis.
        """
        print("Welcome to the Document Generator!")

        # Step 1: Initialize the LLM manager to ensure a connection.
        print("\n=== Step 1: Initializing Language Model ===")
        if not self.llm_manager.initialize_llm(model_name):
            print("Failed to initialize the language model. Aborting.")
            return

        # Step 2: Load and split documents into chunks.
        print("\n=== Step 2: Loading and Splitting Documents into Chunks ===")
        # Get model-specific details for the splitter.
        max_chunk: int = self.llm_manager.model_max_chunk(model_name)
        token_counter: Callable[..., int] = self.llm_manager.count_tokens
        documents: Dict[str, List[Document]] = self.document_splitter.split_documents(
            file_path=file_path,
            chunk_size=max_chunk,
            token_counter=token_counter,
        )
        if not documents:
            print("No documents were processed. Aborting.")
            return

        # Step 3: Create an analysis prompt for each document.
        print("\n=== Step 3: Creating Prompts for Each Document ===")
        if self.prompt_generator.create_analysis_prompts(documents=documents):
            prompts: Dict[str, Dict[str, Tuple[Document, PromptTemplate]]] = self.prompt_generator.get_documents
        else:
            print("Failed to generate prompts. Aborting.")
            return

        # Step 4: Send the code and prompt to the LLM for analysis.
        print("\n=== Step 4: Analyzing Documents using Langchain Chain ===")
        llm: ChatOllama = self.llm_manager.get_llm_model()
        document: Document
        prompt: PromptTemplate
        processed_documents: Dict[str, Dict[str, List[Document]]] = {}
        # Step 4.1:  Generate Analysis and Structure of the Code.
        print("\t=== Step 4.1: Generate Analysis and Structure of the Code ===")
        for document_name, document_data in prompts.items():
            # --- Process Analysis Prompt (if it exists) ---
            if "analysis" in document_data:
                document, prompt = document_data["analysis"]
                chain: Runnable = prompt | llm.with_structured_output(Code_Analysis)
                print(f"\tAnalyzing Document: {document_name}")
                analysis_result: Dict | BaseModel = chain.invoke({"page_content": document.page_content})
                if isinstance(analysis_result, Code_Analysis):
                    page_content = f"## Code Analysis\n\n ### **Summary**:\n{analysis_result.summary}\n\n### **Analysis**:\n{analysis_result.analysis}"
                    processed_documents.setdefault(document_name, {})["analysis"] = [Document(metadata=document.metadata, page_content=page_content)]
                    print(f"\tSuccessfully stored analysis for {document_name}")
                else:
                    print(f"\t[ERROR] Unexpected result type for analysis of {document_name}: {type(analysis_result)}")

            # --- Process Structure Prompt (if it exists) ---
            if "structure" in document_data:
                document, prompt = document_data["structure"]
                chain: Runnable = prompt | llm.with_structured_output(Code_Structure)
                print(f"\tStructuring Document: {document_name}")
                structure_result: Dict | BaseModel = chain.invoke({"page_content": document.page_content})
                if isinstance(structure_result, Code_Structure):
                    # Assuming result.page_content holds the structured output
                    page_content: str = f"## Code Structure\n\n{structure_result.page_content}"
                    processed_documents.setdefault(document_name, {})["structure"] = [Document(metadata=document.metadata, page_content=page_content)]
                    print(f"\tSuccessfully stored structure for {document_name}")
                else:
                    print(f"\t[ERROR] Unexpected result type for structure of {document_name}: {type(structure_result)}")

        # Step 4.2:  Generate Technical Specification of the Code.
        print("\t=== Step 4.2: Generate Technical Specification of the Code ===")
        if self.prompt_generator.create_specification_prompts(processed_documents=processed_documents):
            prompts: Dict[str, Dict[str, Tuple[Document, PromptTemplate]]] = self.prompt_generator.get_documents
            for document_name, document_data in prompts.items():
                # --- Process Technical Specification Prompt (if it exists) ---
                if "specification" in document_data:
                    document, prompt = document_data["specification"]
                    chain: Runnable = prompt | llm
                    print(f"\tGenerating Technical Specification Document: {document_name}")
                    specification_result: Dict | BaseModel = chain.invoke({"page_content": document.page_content})
                    if hasattr(specification_result, "content"):
                        page_content = f"## Technical Specification\n\n{specification_result.content}"
                        print(specification_result.content)
                        processed_documents.setdefault(document_name, {})["specification"] = [Document(metadata=document.metadata, page_content=page_content)]
                        print(f"\tSuccessfully stored specification for {document_name}")
                    elif isinstance(specification_result, Technical_Specification):
                        page_content = f"## Technical Specification\n\n{specification_result.page_content}"
                        print(specification_result.page_content)
                        processed_documents.setdefault(document_name, {})["specification"] = [Document(metadata=document.metadata, page_content=page_content)]
                        print(f"\tSuccessfully stored specification for {document_name}")
                    else:
                        print(f"\t[ERROR] Unexpected result type for specification of {document_name}: {type(specification_result)}")
        else:
            print("\tFailed to generate prompts. Aborting.")
            return

        # Step 5: Assemble the analyzed content into a final Markdown document.
        print("\n=== Step 5: Creating Markdown Document ===")
        if self.document_creator.create_markdown(
            documents=processed_documents,
            output_filename=output_file_path,
        ):
            print(f"Markdown document created successfully at {output_file_path}")
        else:
            print("Failed to create the final markdown document.")
