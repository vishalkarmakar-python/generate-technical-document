"""
Entry point for the document generation application.

This script initializes and runs the document generation process. It uses the
`argparse` library to handle command-line arguments for the source code
directory, the output directory, and the language model name, providing
sensible defaults from the application's configuration.
"""

from app.config import (
    DEFAULT_INPUT_PATH,
    DEFAULT_MODEL_NAME,
    DEFAULT_OUTPUT_PATH,
)
from app.create_document import CreateDocument
from app.document_splitter import Document_Splitter
from app.generate_document import Generate
from app.language_model import Ollama
from app.prompt_generator import PromptGenerator
from argparse import ArgumentParser, Namespace
from typing import Any


def main() -> None:
    """
    Main function to orchestrate the code analysis and document generation.

    It parses command-line arguments for file paths and the model name,
    and then initiates the generation process by calling the `run` method
    of the `Generate` class.
    """
    # Initialize the argument parser with a description of the application.
    parser = ArgumentParser(description="Analyze ABAP source code and generate Markdown documentation.")
    parser.add_argument("--file_path", type=str, default=None, help="Path to the code files. Optional.")
    parser.add_argument("--output_path", type=str, default=None, help="Path for the output files. Optional.")
    parser.add_argument("--model", type=str, default=None, help="Name of the language model. Optional.")
    # Parse the arguments provided at the command line.
    args: Namespace = parser.parse_args()

    # If arguments are not provided via command line, prompt the user interactively.
    file_path: Any | str = args.file_path or input(f"Enter the path for the code files (default: {DEFAULT_INPUT_PATH}): ").strip() or DEFAULT_INPUT_PATH
    output_path: Any | str = args.output_path or input(f"Enter the output file path (default: {DEFAULT_OUTPUT_PATH}): ").strip() or DEFAULT_OUTPUT_PATH
    model_name: Any | str = args.model or input(f"Enter the model name (default: {DEFAULT_MODEL_NAME}): ").strip() or DEFAULT_MODEL_NAME

    # --- Application Composition Root ---
    # Instantiate all the components of the application.
    document_splitter: Document_Splitter = Document_Splitter()
    llm_manager: Ollama = Ollama()
    prompt_generator: PromptGenerator = PromptGenerator()
    document_creator: CreateDocument = CreateDocument()
    # Instantiate the main orchestrator, injecting the components.
    app = Generate(
        document_splitter=document_splitter,
        llm_manager=llm_manager,
        prompt_generator=prompt_generator,
        document_creator=document_creator,
    )
    # Run the application workflow.
    app.run(
        file_path=file_path,
        output_file_path=output_path,
        model_name=model_name,
    )


if __name__ == "__main__":
    main()
