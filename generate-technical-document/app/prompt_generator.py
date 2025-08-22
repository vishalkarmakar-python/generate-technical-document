"""
Generates tailored prompts for different types of ABAP objects by loading
templates from external files and selecting them dynamically.
"""

from app.language_separator import ABAP
from langchain_core.documents.base import Document
from langchain_core.prompts import PromptTemplate
from pathlib import Path
from typing import ClassVar, Dict, List, Self, Tuple


class PromptGenerator:
    """
    Creates specific LLM prompts for ABAP code analysis.

    This class loads prompt templates from an external 'prompts' directory
    upon initialization. It then dynamically assigns the correct prompt to a
    document based on its categorized type, making the system scalable and
    easy to maintain.
    """

    _instance: ClassVar[Self | None] = None
    _PROMPTS_DIR: Path = Path(__file__).parent.parent / "prompts"

    def __new__(cls) -> Self:
        """Ensures that only one instance of PromptGenerator is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the PromptGenerator, loading all prompt templates from disk.
        """
        if not hasattr(self, "_initialized"):
            self._initialized: bool = True
            self._prompts: Dict[str, Dict[str, Tuple[Document, PromptTemplate]]] = {}
            self._load_prompt_templates()

            # Map document categories to their corresponding template file names.
            # This makes adding new categories and prompts much easier.
            self._category_to_template_map: Dict[str, str] = {
                "ANALYSIS": "analysis_summary_template.md",
                "DATABASE": "structure_database_template.md",
                "OBJECT ORIENTED": "structure_class_template.md",
                "FUNCTION MODULE": "structure_function_module_template.md",
                "CLASSICAL": "structure_report_program_template.md",
                "RAP FRAMEWORK": "structure_behavior_template.md",
                "SPECIFICATION": "technical_specification_template.md",
            }

    def _load_prompt_templates(self) -> None:
        """
        Loads all .md files from the prompts directory into memory.
        """
        self._prompt_templates: Dict[str, str] = {}
        if not self._PROMPTS_DIR.is_dir():
            print(f"[WARNING] Prompts directory not found at: {self._PROMPTS_DIR}")
            return

        for file_path in self._PROMPTS_DIR.glob("*.md"):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self._prompt_templates[file_path.name] = file.read()
                print(f"[INFO] Loaded prompt template: {file_path.name}")
            except IOError as error:
                print(f"[ERROR] Failed to load prompt {file_path.name}: {error}")

    def create_analysis_prompts(self, documents: Dict[str, List[Document]]) -> bool:
        """
        Creates and assigns analysis and structure prompts for each document in a single pass.

        Args:
            documents: A dictionary of documents from the `Document_Splitter`.

        Returns:
            True if any prompts were successfully created, False otherwise.
        """
        for document_name, document_list in documents.items():
            print(f"Creating prompts for document: {document_name}")
            if not document_list or not hasattr(document_list[0], "metadata"):
                continue

            document: Document = document_list[0]  # Use the first document chunk

            # --- 1. Create Analysis Prompt ---
            analysis_template_file: str | None = self._category_to_template_map.get("ANALYSIS")
            if analysis_template_file:
                template_string: str | None = self._prompt_templates.get(analysis_template_file)
                if template_string:
                    prompt = PromptTemplate(input_variables=["page_content"], template=template_string)
                    self._prompts.setdefault(document_name, {})["analysis"] = (document, prompt)
                else:
                    print(f"[WARNING] Analysis template file '{analysis_template_file}' not found.")

            # --- 2. Create Structure Prompt ---
            document_type: str = document.metadata.get("document_type", "GENERIC")
            assigned_category: str = "GENERIC"  # Default
            for category, types_list in ABAP.get_document_categories().items():
                if document_type in types_list:
                    assigned_category = category
                    break

            structure_template_file: str | None = self._category_to_template_map.get(assigned_category)
            if structure_template_file:
                template_string = self._prompt_templates.get(structure_template_file)
                if template_string:
                    prompt = PromptTemplate(input_variables=["page_content"], template=template_string)
                    self._prompts.setdefault(document_name, {})["structure"] = (document, prompt)
                else:
                    print(f"[WARNING] Structure template file '{structure_template_file}' not found.")

        return bool(self._prompts)

    def create_specification_prompts(self, processed_documents: Dict[str, Dict[str, List[Document]]]) -> bool:
        """
        Creates technical specification prompts using the generated analysis and structure.
        """
        spec_template_file: str | None = self._category_to_template_map.get("SPECIFICATION")
        if not spec_template_file:
            print("[WARNING] Technical specification template not found in map.")
            return False

        template_string: str | None = self._prompt_templates.get(spec_template_file)
        if not template_string:
            print(f"[WARNING] Specification template file '{spec_template_file}' not found.")
            return False

        for doc_name, data in processed_documents.items():
            analysis_content: str = data.get("analysis", [Document(page_content="")])[0].page_content
            structure_content: str = data.get("structure", [Document(page_content="")])[0].page_content
            # Combine analysis and structure to form the context
            page_content: str = f"## Code Analysis\n{analysis_content}\n\n## Code Structure\n{structure_content}"
            prompt = PromptTemplate(input_variables=["page_content"], template=template_string)
            document: Document = data["analysis"][0] if "analysis" in data else data["structure"][0]
            self._prompts.setdefault(doc_name, {})["specification"] = (Document(page_content=page_content, metadata=document.metadata), prompt)
            print(f"\tCreating specification prompt for document: {doc_name}")

        return True

    @property
    def get_documents(self) -> Dict[str, Dict[str, Tuple[Document, PromptTemplate]]]:
        """
        Extracts and returns documents from the central prompt dictionary.
        This maintains compatibility with the calling code.
        """
        return self._prompts

    @property
    def get_analysis_documents(self) -> Dict[str, Tuple[Document, PromptTemplate]]:
        """
        Extracts and returns only the analysis documents from the central prompt dictionary.
        This maintains compatibility with the calling code.
        """
        return {doc_name: data["analysis"] for doc_name, data in self._prompts.items() if "analysis" in data}

    @property
    def get_structure_documents(self) -> Dict[str, Tuple[Document, PromptTemplate]]:
        """
        Extracts and returns only the structure documents from the central prompt dictionary.
        This maintains compatibility with the calling code.
        """
        return {doc_name: data["structure"] for doc_name, data in self._prompts.items() if "structure" in data}

    @property
    def get_specification_documents(self) -> Dict[str, Tuple[Document, PromptTemplate]]:
        """
        Extracts and returns only the specification documents from the central prompt dictionary.
        This maintains compatibility with the calling code.
        """
        return {doc_name: data["specification"] for doc_name, data in self._prompts.items() if "specification" in data}

    @property
    def clear_documents(self) -> bool:
        """Clears the stored documents and prompts."""
        self._prompts.clear()
        return True
