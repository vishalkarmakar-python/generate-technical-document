"""
Handles the creation of the final Markdown analysis report.

This module contains the `CreateDocument` class, which is responsible for
aggregating the analysis results from various code documents into a single,
well-formatted Markdown file.
"""

from langchain_core.documents.base import Document
from os import path
from typing import Dict, List


class CreateDocument:
    """
    Generates a Markdown document from analysis results.

    This class compiles the generated analysis content for each source code file
    into a single Markdown report, complete with titles and separators for
    readability.
    """

    def create_markdown(
        self,
        documents: Dict[str, Dict[str, List[Document]]],
        output_filename: str,
    ) -> bool:
        """
        Generates and writes the final Markdown file in a stateless manner.

        This method iterates through the dictionary of analyzed documents, formats
        them, and writes the combined content to a file. It uses a local
        variable to store the content, ensuring that each call is independent
        and produces a correct document.

        Args:
            documents: A dictionary where keys are original filenames and values
                       are lists of LangChain `Document` objects containing the
                       analysis content.
            output_filename: The directory path where the output Markdown file
                             will be saved.

        Returns:
            True if the file was written successfully, False otherwise.
        """
        # Use a local variable for the content, making the method stateless.
        markdown_content: List[str] = []

        # Iterate through each original file and its corresponding analysis documents.
        for document_name, document_data in documents.items():
            # Start with a main title for the report for the current file.
            markdown_content.append(f"# Code Analysis Report: `{document_name.upper()}`")

            # Analysis.
            analysis_document: List[Document] | None = document_data.get("analysis")
            if analysis_document:
                markdown_content.append("---")
                markdown_content.append(analysis_document[0].page_content)
                markdown_content.append("\n---\n")  # Separator at the end of the file's section.

            # Structure
            structure_document: List[Document] | None = document_data.get("structure")
            if structure_document:
                markdown_content.append("---")
                markdown_content.append(structure_document[0].page_content)
                markdown_content.append("\n---\n")  # Separator at the end of the file's section.

            # Technical Specification
            specification_document: List[Document] | None = document_data.get("specification")
            if specification_document:
                markdown_content.append("---")
                markdown_content.append(specification_document[0].page_content)
                markdown_content.append("\n---\n")  # Separator at the end of the file's section.

        # Construct the full path for the output Markdown file.
        output_path: str = path.join(output_filename, "code_structure.md")
        try:
            # Write the collected Markdown content to the file.
            with open(file=output_path, mode="w", encoding="utf-8") as file:
                file.write("\n".join(markdown_content))
            print(f"Successfully created Markdown file: {output_path}")
            return True
        except IOError as error:
            # Handle potential file writing errors.
            print(f"Error writing to file {output_path}: {error}")
            return False
