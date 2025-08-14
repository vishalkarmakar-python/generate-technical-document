"""
Handles the creation of the final Markdown analysis report.

This module contains the `CreateDocument` class, which is responsible for
aggregating the analysis results from various code documents into a single,
well-formatted Markdown file.
"""

from langchain_core.documents.base import Document
from os import path
from typing import ClassVar, Dict, List, Self


class CreateDocument:
    """
    A singleton class to generate a Markdown document from analysis results.

    This class compiles the generated analysis content for each source code file
    into a single Markdown report, complete with titles and separators for
    readability. The singleton pattern ensures a consistent state for the
    markdown content being generated.
    """

    _instance: ClassVar[Self | None] = None

    def __new__(cls) -> Self:
        """
        Ensures that only one instance of CreateDocument is created (Singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the CreateDocument instance.

        The `_initialized` flag prevents reinitialization of the markdown content
        list if the instance is accessed multiple times.
        """
        if not hasattr(self, "_initialized"):
            self._initialized: bool = True
            self._markdown_content: List[str] = []

    def create_markdown(
        self,
        documents: Dict[str, List[Document]],
        output_filename: str,
    ) -> bool:
        """
        Generates and writes the final Markdown file.

        It iterates through the dictionary of analyzed documents, formats them
        with appropriate headers, and writes the combined content to a file named
        'code_structure.md' in the specified output directory.

        Args:
            documents: A dictionary where keys are original filenames and values
                       are lists of LangChain `Document` objects containing the
                       analysis content.
            output_filename: The directory path where the output Markdown file
                             will be saved.

        Returns:
            True if the file was written successfully, False otherwise.
        """
        overall_success: bool = True
        # Iterate through each original file and its corresponding analysis documents.
        for filename, document in documents.items():
            # Start with a main title for the report for the current file.
            self._markdown_content.append(f"# Code Analysis Report: `{filename.upper()}`")
            self._markdown_content.append("---")
            # Process each generated document chunk (which contains analysis or summary).
            for document_chunk in document:
                self._markdown_content.append(document_chunk.page_content)
                self._markdown_content.append("\n")  # Add spacing for readability.

            self._markdown_content.append("\n---\n")  # Separator at the end of the file's section.

        # Construct the full path for the output Markdown file.
        output_path: str = path.join(output_filename, "code_structure.md")
        try:
            # Write the collected Markdown content to the file.
            with open(file=output_path, mode="w", encoding="utf-8") as file:
                file.write("\n".join(self._markdown_content))
            print(f"Successfully created Markdown file: {output_path}")
        except IOError as error:
            # Handle potential file writing errors.
            print(f"Error writing to file {output_path}: {error}")
            overall_success = False

        return overall_success
