"""
Orchestrates the entire code analysis and documentation generation pipeline.

This module contains the `Generate` class, which acts as the main controller,
coordinating all steps from loading source files to generating the final
Markdown report.
"""

from app.create_document import CreateDocument
from app.document_splitter import Document_Splitter
from app.language_model import Ollama
from app.prompt_generator import PromptGenerator
from app.structured_output import Analysis
from langchain_core.documents.base import Document
from langchain_core.language_models import LanguageModelInput
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from pydantic import BaseModel
from typing import ClassVar, Dict, List, Self, Tuple, Union


class Generate:
    """
    A singleton class that manages the end-to-end document generation process.

    This class integrates all components of the application:
    1. `Document_Splitter`: To load and chunk the source code.
    2. `PromptGenerator`: To create tailored prompts for the LLM.
    3. `Ollama`: To interact with the language model.
    4. `CreateDocument`: To assemble the final report.
    The singleton pattern ensures all steps use the same configuration and state.
    """

    _instance: ClassVar[Self | None] = None

    def __new__(cls) -> Self:
        """
        Ensures that only one instance of Generate is created (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the Generate instance.

        The `_initialized` flag prevents reinitialization of attributes.
        It sets up placeholders for the LLM and the LangChain runnable chain.
        """
        if not hasattr(self, "_initialized"):
            self._initialized: bool = True
            self._llm: Runnable[LanguageModelInput, Union[Dict, BaseModel]]
            self._chain: Runnable

    @classmethod
    def run(cls, file_path: str, output_file_path: str, model_name: str) -> None:
        """
        Executes the full document generation pipeline.

        This is the main entry point of the application logic. It proceeds
        through four distinct steps to generate the analysis report.

        Args:
            file_path: The directory containing the ABAP source code files.
            output_file_path: The directory where the final Markdown report
                              will be saved.
            model_name: The name of the Ollama model to use for analysis.
        """
        # Start of Application
        print("Welcome to the Document Generator!")

        # Step 1: Load ABAP code from files and split them into manageable chunks.
        print("\n=== Step 1: Loading and Splitting Documents into Chunks ===")
        cls._splitter: Document_Splitter = Document_Splitter()
        if cls._splitter.split_documents(file_path=file_path, model_name=model_name):
            cls._documents: Dict[str, List[Document]] = cls._splitter.get_documents

        # Step 2: Create a specific, detailed prompt for each document chunk.
        print("\n=== Step 2: Creating Prompts for Each Document ===")
        cls._prompt: PromptGenerator = PromptGenerator()
        if cls._prompt.create_prompt(documents=cls._documents):
            cls._prompts: Dict[str, Tuple[Document, PromptTemplate]] = cls._prompt.get_documents

        # Step 3: Send the code and prompt to the LLM for analysis.
        print("\n=== Step 3: Analyzing Documents using Langchain Chain ===")
        cls._ollama: Ollama = Ollama()
        if cls._ollama.initialize_llm(model_name=model_name):
            for document_name, (document, prompt) in cls._prompts.items():
                # Get the initialized LLM model.
                cls._llm = cls._ollama.get_llm_model()
                # Create the LangChain processing chain (prompt -> LLM).
                cls._chain = prompt | cls._llm
                print(f"Analyzing document for:\n{document_name}")
                # Invoke the chain to get the analysis result.
                result: Dict | BaseModel = cls._chain.invoke({"page_content": document.page_content})

                # Process the result from the LLM. It can be a Pydantic model or a generic object.
                if isinstance(result, Analysis):
                    # Handle structured output via Pydantic model.
                    if cls._splitter.create_document(document_name=document_name, document_metadata=document.metadata, page_content=str(result.page_content)):
                        print(f"{result.page_content}:")
                    else:
                        print(f"Failed to create document for {document_name}")
                elif hasattr(result, "content"):
                    # Handle standard LLM content attribute.
                    if cls._splitter.create_document(document_name=document_name, document_metadata=document.metadata, page_content=str(result.content)):
                        print(f"{result.content}:")
                    else:
                        print(f"Failed to create document for {document_name}")
                print(result.content)

        # Step 4: Assemble the analyzed content into a final Markdown document.
        print("\n=== Step 4: Create Markdown Document ===")
        cls._create_document: CreateDocument = CreateDocument()
        if cls._create_document.create_markdown(documents=cls._splitter.get_analyzed_documents, output_filename=output_file_path):
            print(f"Markdown document created successfully at {file_path}")
