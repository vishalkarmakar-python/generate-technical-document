"""
Entry point for the document generation application.

This script initializes and runs the document generation process. It prompts the
user for the source code directory, the output directory for the generated
markdown files, and the name of the language model to use for analysis.
It provides default values for easier testing and execution.
"""

from app.generate_document import Generate


def main() -> None:
    """
    Main function to orchestrate the code analysis and document generation.

    It gathers necessary inputs from the user, such as file paths and the model
    name, and then initiates the generation process by calling the `run` method
    of the `Generate` class.
    """
    # Define default paths for input (code files) and output (markdown files)
    # to simplify execution during development and testing.
    test_input_file_path: str = "C:\\Users\\Vishal Karmakar\\Documents\\SAP\\Artificial-Intelligence\\code-structure\\files\\backup\\"
    test_output_file_path: str = "C:\\Users\\Vishal Karmakar\\Documents\\SAP\\Artificial-Intelligence\\code-structure\\files\\analyzed_documents\\"
    # Define the default language model to be used for code analysis.
    model_name: str = "QWEN"

    # The `Generate.run` method is called to start the application.
    # It takes user input for paths and model name. If the user presses Enter
    # without providing input, the predefined default values are used.
    Generate.run(
        file_path=(input("Enter the path for the code files: ").strip() or test_input_file_path),
        output_file_path=(input("Enter the output file path for markdown files: ").strip() or test_output_file_path),
        model_name=input("Enter the model name: ").strip() or model_name,
    )


if __name__ == "__main__":
    # This standard Python construct ensures that the main() function is called
    # only when the script is executed directly.
    main()
