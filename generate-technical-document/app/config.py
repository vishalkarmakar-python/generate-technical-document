"""
Centralized configuration management for the application.

This module loads settings from the .env file and defines application-wide
constants, such as default file paths and model names. This approach
decouples configuration from the application logic, making it more modular
and easier to manage.
"""

from dotenv import load_dotenv
from os import getenv
from pathlib import Path

# Load environment variables from the .env file.
if load_dotenv():
    # --- Application-Level Constants ---
    # Define the base directory of the project for robust path handling.
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # --- Default Path Configurations ---
    # Define the default directory for input source code files.
    DEFAULT_INPUT_PATH = str(BASE_DIR / "files" / "backup")
    # Define the default directory for outputting analyzed markdown documents.
    DEFAULT_OUTPUT_PATH = str(BASE_DIR / "files" / "analyzed_documents")

    # --- Default Language Model Configuration ---
    # Define the default language model to be used for code analysis.
    DEFAULT_MODEL_NAME: str = getenv("DEFAULT_MODEL_NAME", "MISTRAL")
else:
    # If the .env file is not found or fails to load, an error is raised.
    # This ensures that the application does not run with missing configurations.
    raise EnvironmentError("Failed to load environment variables from .env file.")
