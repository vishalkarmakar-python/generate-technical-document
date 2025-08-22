"""
Initializes the 'app' package and defines its public API.

This file makes the 'app' directory a Python package, allowing for modular
imports. The `__all__` list explicitly declares which class names are part of
the public interface of this package, making them easily importable by other
parts of the application.
"""

from app.create_document import CreateDocument
from app.document_splitter import Document_Splitter
from app.generate_document import Generate
from app.language_model import Ollama
from app.language_separator import ABAP
from app.prompt_generator import PromptGenerator
from app.structured_output import Code_Analysis, Code_Structure, Technical_Specification
from typing import List

# Defines the public API of the 'app' package.
__all__: List[str] = [
    "Document_Splitter",
    "Generate",
    "Ollama",
    "ABAP",
    "PromptGenerator",
    "Code_Analysis",
    "Code_Structure",
    "Technical_Specification",
    "CreateDocument",
]
