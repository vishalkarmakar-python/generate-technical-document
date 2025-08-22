"""
Handles loading, analyzing, and splitting of ABAP source code files.

This module contains the `Document_Splitter` class, which is responsible for:
1. Loading `.abap` files from a directory.
2. Guessing the ABAP object type (e.g., Class, Report, Table) based on keywords.
3. Splitting the document content into manageable chunks.
4. Enriching each chunk with relevant metadata.
"""

from app.language_separator import ABAP
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from typing import Any, Callable, Dict, List


class Document_Splitter:
    """
    Loads and prepares ABAP source documents for analysis.

    This class manages the pre-processing pipeline for source code files before
    they are sent to an LLM. It is designed to be a stateless processor that
    takes a file path and returns structured, chunked documents.
    """

    def __init__(self) -> None:
        """
        Initializes the Document_Splitter instance.
        """
        self._document_directory: List[Document] = []

    def split_documents(
        self,
        file_path: str,
        chunk_size: int,
        token_counter: Callable[[str], int],
    ) -> Dict[str, List[Document]]:
        """
        Loads, analyzes, and splits all documents in the given path.

        This is the main public method that orchestrates the document preparation
        process. It returns a dictionary of processed documents.

        Args:
            file_path: The path to the directory containing ABAP source files.
            chunk_size: The maximum size of each chunk, typically based on the
                        LLM's token limit.
            token_counter: A function that takes a string and returns the
                           number of tokens.

        Returns:
            A dictionary where keys are document names and values are lists of
            split and context-enriched `Document` chunks. Returns an empty
            dictionary if loading fails.
        """
        documents: Dict[str, List[Document]] = {}
        if self._load_documents(file_path=file_path):
            for document_index, document in enumerate(self._document_directory, 1):
                file_stem: str = Path(document.metadata.get("source", "unknown")).stem.lower()
                print(f"Processing document no-{document_index}: {file_stem}")

                document_type: str = self._analyze_document_type(document.page_content)
                print(f"\tDocument Type: {document_type}")
                document_tokens: int = token_counter(document.page_content)
                print(f"\tDocument Token Count: {document_tokens} tokens")
                print(f"\t{'*' * 50}")

                split_document: List[Document] = self._create_splitter(
                    document=document,
                    chunk_size=min(document_tokens, chunk_size),
                )

                documents[file_stem] = self._generate_metadata_for_document(
                    document_metadata=document.metadata.copy(),
                    document_chunks=split_document,
                    document_type=document_type,
                    document_tokens=document_tokens,
                    token_counter=token_counter,
                )
            return documents
        else:
            print("No documents loaded to split.")
            return {}

    def _load_documents(self, file_path: str) -> bool:
        """
        Loads all `.abap` files from the specified directory using DirectoryLoader.
        """
        try:
            print(f"Loading code files from directory: {file_path}")
            self._document_directory = DirectoryLoader(
                path=str(file_path),
                glob="**/*.abap",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8", "autodetect_encoding": True},
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
        """
        content_lower: str = content.lower()
        best_match: Dict[str, Any] = {"doc_type": "GENERIC_ABAP", "match_percentage": 0.0}

        for doc_type, keywords in ABAP.get_document_keywords().items():
            matched_keywords: List[str] = [kw.lower() for kw in keywords if kw.lower() in content_lower]
            match_percentage: float = len(matched_keywords) / len(keywords) if keywords else 0.0

            if match_percentage > best_match["match_percentage"]:
                best_match = {"doc_type": doc_type, "match_percentage": match_percentage}

        return best_match["doc_type"]

    def _create_splitter(self, document: Document, chunk_size: int) -> List[Document]:
        """
        Creates and applies a text splitter to a document.
        """
        splitter = RecursiveCharacterTextSplitter(
            separators=ABAP.get_separators(),
            chunk_size=chunk_size,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=True,
            keep_separator=True,
        )
        return splitter.split_documents(documents=[document])

    def _generate_metadata_for_document(
        self,
        document_chunks: List[Document],
        document_type: str,
        document_metadata: Dict,
        document_tokens: int,
        token_counter: Callable[[str], int],
    ) -> List[Document]:
        """
        Enriches each document chunk with additional metadata.
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
                    "chunk_token_count": token_counter(document_chunk.page_content),
                    "is_first_chunk": chunk_index == 1,
                    "is_last_chunk": chunk_index == len(document_chunks),
                    "is_single_chunk": len(document_chunks) == 1,
                }
            )
            chunks_with_context.append(Document(metadata=chunk_metadata, page_content=document_chunk.page_content))
        return chunks_with_context
