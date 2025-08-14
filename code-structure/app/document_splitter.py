"""
Handles loading, analyzing, and splitting of ABAP source code files.

This module contains the `Document_Splitter` class, which is responsible for:
1. Loading `.abap` files from a directory.
2. Guessing the ABAP object type (e.g., Class, Report, Table) based on keywords.
3. Splitting the document content into manageable chunks for the LLM.
4. Enriching each chunk with relevant metadata.
"""

from app.language_model import Ollama
from app.language_separator import ABAP
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Self


class Document_Splitter:
    """
    A singleton class for loading and preparing ABAP source documents.

    This class manages the entire pre-processing pipeline for source code files
    before they are sent to the LLM. The singleton pattern ensures that document
    states (like loaded documents and analyzed documents) are managed centrally.
    """

    _instance: ClassVar[Self | None] = None

    def __new__(cls) -> Self:
        """Ensures that only one instance of Document_Splitter is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the Document_Splitter instance.

        The `_initialized` flag ensures that the instance's lists and dictionaries
        are set up only once.
        """
        if not hasattr(self, "_initialized"):
            self._initialized: bool = True
            self._document_directory: List[Document] = []
            self._documents: Dict[str, List[Document]] = {}
            self._analyzed_document: Dict[str, List[Document]] = {}

    def split_documents(
        self,
        file_path: str,
        model_name: str,
    ) -> bool:
        """
        Loads, analyzes, and splits all documents in the given path.

        This is the main public method that orchestrates the document preparation
        process. It returns a dictionary of processed documents.

        Args:
            file_path: The path to the directory containing ABAP source files.
            model_name: The name of the language model, used to determine the
                        maximum token limit for splitting.

        Returns:
            True if documents were successfully processed, False otherwise.
        """
        if self._load_documents(file_path=file_path):
            for document_index, document in enumerate(self._document_directory, 1):
                file_stem: str = Path(document.metadata.get("source", "unknown")).stem.lower()
                print(f"Processing document no-{document_index}: {file_stem}")

                # Analyze document content to guess the ABAP object type.
                document_type: str = self._analyze_document_type(document.page_content)
                print(f"\tDocument Type: {document_type}")
                document_tokens: int = Ollama.count_tokens(content=document.page_content)
                print(f"\tDocument Token Count: {document_tokens} tokens")
                max_tokens: int = Ollama.model_max_token(model_name=model_name)
                print(f"\t{'*' * 50}")

                # Split the document using a chunk size that respects the model's limit.
                split_document: List[Document] = self._create_splitter(
                    document=document,
                    chunk_size=min(document_tokens, max_tokens),
                )

                # Add rich context (e.g., chunk index, token count) to each chunk's metadata.
                self._documents[file_stem] = self._generate_context_for_document_chunks(
                    document_metadata=document.metadata.copy(),
                    document_chunks=split_document,
                    document_type=document_type,
                    document_tokens=document_tokens,
                )
            return True if self._documents else False
        else:
            print("No documents loaded to split.")
            return False

    def _load_documents(self, file_path: str) -> bool:
        """
        Loads all `.abap` files from the specified directory using DirectoryLoader.

        Args:
            file_path: The directory path to load files from.

        Returns:
            True if documents were loaded, False if no documents were found.

        Raises:
            RuntimeError: If there is an issue during file loading.
        """
        try:
            print(f"Loading code files from directory: {file_path}")
            # Use LangChain's DirectoryLoader to efficiently load all .abap files.
            self._document_directory = DirectoryLoader(
                path=str(file_path),
                glob="**/*.abap",  # Search recursively for .abap files
                loader_cls=TextLoader,
                loader_kwargs={
                    "encoding": "utf-8",
                    "autodetect_encoding": True,
                },
                show_progress=True,
                silent_errors=True,
            ).load()

            if self._document_directory:
                print(f"{len(self._document_directory)} Code files loaded successfully from '{file_path}'")
                return True
            else:
                print("No code files found in the specified directory.")
                return False

        except Exception as error:
            raise RuntimeError(f"Error loading documents: {error}")

    def _analyze_document_type(self, content: str) -> str:
        """
        Analyzes the document content to determine the ABAP object type.

        It compares the content against a predefined set of keywords associated
        with different ABAP object types and returns the best match.

        Args:
            content: The source code content of the document.

        Returns:
            A string representing the determined document type (e.g., "CLASS").
        """
        content_lower: str = content.lower()
        best_match: Dict[str, Any] = {"doc_type": "GENERIC_ABAP", "match_percentage": 0.0}

        # Iterate through all known ABAP document types and their keywords.
        for doc_type, keywords in ABAP.get_document_keywords().items():
            matched_keywords: List[str] = [kw.lower() for kw in keywords if kw.lower() in content_lower]
            matched_count: int = len(matched_keywords)
            total_keywords: int = len(keywords)
            match_percentage: float = matched_count / total_keywords if total_keywords > 0 else 0.0

            # If this type is a better match than the current best, update it.
            if match_percentage > best_match["match_percentage"]:
                best_match = {"doc_type": doc_type, "match_percentage": match_percentage}

        return best_match["doc_type"]

    def _create_splitter(self, document: Document, chunk_size: int) -> List[Document]:
        """
        Creates and applies a text splitter to a document.

        It uses a `RecursiveCharacterTextSplitter` with ABAP-specific separators
        to intelligently chunk the code.

        Args:
            document: The document to be split.
            chunk_size: The maximum size of each chunk.

        Returns:
            A list of `Document` objects, where each is a chunk of the original.
        """
        splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
            separators=ABAP.get_separators(),
            chunk_size=chunk_size,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=True,
            keep_separator=True,
        )
        return splitter.split_documents(documents=[document])

    def _generate_context_for_document_chunks(
        self,
        document_chunks: List[Document],
        document_type: str,
        document_metadata: Dict,
        document_tokens: int,
    ) -> List[Document]:
        """
        Enriches each document chunk with additional metadata.

        This metadata provides valuable context for the LLM, such as the document's
        name, type, token counts, and chunk position.

        Args:
            document_chunks: The list of chunks to enrich.
            document_type: The determined type of the source document.
            document_metadata: The original metadata from the loaded document.
            document_tokens: The total token count of the original document.

        Returns:
            A list of `Document` chunks with enriched metadata.
        """
        chunks_with_context: List[Document] = []
        for chunk_index, document_chunk in enumerate(document_chunks, 1):
            chunk_metadata: Dict[Any, Any] = document_metadata.copy()
            chunk_metadata.update(
                {
                    "document_name": Path(document_metadata.get("source", "unknown")).stem.lower(),
                    "document_type": document_type,
                    "document_tokens": document_tokens,
                    "chunk_index": chunk_index,
                    "chunk_id": f"{Path(document_metadata.get('source', 'unknown')).stem.lower()}_chunk_{chunk_index}",
                    "chunk_token_count": Ollama.count_tokens(content=document_chunk.page_content),
                    "is_first_chunk": chunk_index == 1,
                    "is_last_chunk": chunk_index == len(document_chunks),
                    "is_single_chunk": len(document_chunks) == 1,
                }
            )
            chunks_with_context.append(Document(metadata=chunk_metadata, page_content=document_chunk.page_content))
        return chunks_with_context

    def create_document(self, document_name: str, document_metadata: Dict, page_content: str) -> bool:
        """
        Stores the analyzed content from the LLM.

        This method takes the analysis result from the LLM and stores it in the
        `_analyzed_document` dictionary, ready for final report generation.

        Args:
            document_name: The name of the document that was analyzed.
            document_metadata: The metadata associated with the document.
            page_content: The analysis content generated by the LLM.

        Returns:
            True if the analyzed document was stored successfully.
        """
        self._analyzed_document[document_name] = [
            Document(
                metadata=document_metadata,
                page_content=page_content,
            )
        ]
        return True if self._analyzed_document.get(document_name) else False

    @property
    def is_initialized(self) -> bool:
        """Returns True if the instance has been initialized."""
        return self._initialized

    @property
    def get_documents(self) -> Dict[str, List[Document]]:
        """Returns the dictionary of split and context-enriched documents."""
        return self._documents

    @property
    def get_analyzed_documents(self) -> Dict[str, List[Document]]:
        """Returns the dictionary of documents after analysis by the LLM."""
        return self._analyzed_document

    @property
    def clear_documents(self) -> bool:
        """
        Clears all stored document data and resets the initialized state.
        """
        self._document_directory.clear()
        self._documents.clear()
        self._analyzed_document.clear()
        self._initialized = False
        return True
