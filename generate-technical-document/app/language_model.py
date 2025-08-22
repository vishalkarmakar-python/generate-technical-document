"""
Manages the connection and interaction with the Ollama language model.

This module provides a singleton wrapper class `Ollama` for the LangChain
`ChatOllama` instance. It handles loading configuration from environment
variables, initializing the model, testing the connection, and providing
helper utilities like token counting.
"""

from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_core.messages.base import BaseMessage
from langchain_ollama import ChatOllama
from os import getenv
from tiktoken import Encoding, get_encoding
from typing import ClassVar, Dict, Self

# Load environment variables once when the module is imported.
load_dotenv()


@dataclass(frozen=True, order=True)
class ModelConfig:
    """A structured container for model-specific configuration."""

    name: str
    max_tokens: int
    max_chunk: int


class Ollama:
    """
    A singleton class to manage and provide access to a ChatOllama instance.

    This class is responsible for managing the lifecycle of the connection to
    the Ollama server, ensuring that a single, shared instance is used
    throughout the application.
    """

    _instance: ClassVar[Self | None] = None

    def __new__(cls) -> Self:
        """Ensures that only one instance of Ollama is created."""
        if cls._instance is None:
            cls._instance = super(Ollama, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the Ollama instance and loads all configurations.
        """
        if not hasattr(self, "_initialized"):
            self._initialized: bool = False
            self._is_connected: bool = False
            self._llm: ChatOllama
            self._load_all_configs()

    def _load_all_configs(self) -> None:
        """Loads all model configurations from environment variables."""
        self.base_url: str = getenv("OLLAMA_MODEL_BASE_URL", "http://localhost:11434")
        self.temperature = float(getenv("OLLAMA_MODEL_TEMPERATURE", 0.1))
        self.num_gpu = int(getenv("OLLAMA_GPU", 8))

        self.model_configs: Dict[str, ModelConfig] = {}
        for model_key in ["QWEN", "GEMMA", "LLAMA", "DEEPSEEK", "CODELLAMA", "MISTRAL"]:  # Use a different variable name for clarity
            model_name: str | None = getenv(f"OLLAMA_MODEL_{model_key}")
            max_tokens: str | None = getenv(f"OLLAMA_MODEL_{model_key}_MAX_TOKENS")
            max_chunk: str | None = getenv(f"OLLAMA_MODEL_{model_key}_MAX_CHUNK")

            if model_name and max_tokens and max_chunk:
                # Use the consistent key (e.g., "QWEN") for the dictionary
                self.model_configs[model_key] = ModelConfig(
                    name=model_name,
                    max_tokens=int(max_tokens),
                    max_chunk=int(max_chunk),
                )

    def initialize_llm(self, model_name: str) -> bool:
        """
        Creates and tests the ChatOllama instance for a specific model.

        Args:
            model_name: The key of the model to initialize (e.g., "QWEN").

        Returns:
            True if initialization is successful, False otherwise.
        """
        config: ModelConfig | None = self.model_configs.get(model_name.upper())
        if not config:
            print(f"[ERROR] Configuration for model '{model_name}' not found.")
            return False

        try:
            self._llm = self._create_llm_instance(config)
            self._is_connected = self._test_connection()
            self._initialized = self._is_connected
            return self._is_connected
        except Exception as error:
            print(f"[ERROR] Ollama initialization failed: {str(error)}")
            return False

    def get_llm_model(self) -> ChatOllama:
        """Provides access to the initialized ChatOllama model instance."""
        if not self._initialized or not hasattr(self, "_llm"):
            raise Exception("LLM not initialized. Call initialize_llm() first.")
        return self._llm

    def _create_llm_instance(self, config: ModelConfig) -> ChatOllama:
        """Creates an instance of the ChatOllama model."""
        return ChatOllama(
            model=config.name,
            base_url=self.base_url,
            temperature=self.temperature,
            num_ctx=config.max_tokens,
            num_predict=config.max_tokens,
            num_gpu=self.num_gpu,
            top_k=2,
            top_p=0.5,
        )

    def _test_connection(self) -> bool:
        """Sends a simple test message to the LLM to verify the connection."""
        try:
            test_message = "Hello, respond with one word."
            response: BaseMessage = self._llm.invoke(input=test_message)
            if response and response.content:
                print("[INFO] Model connection test successful")
                return True
            else:
                print("[WARNING] Model connection test returned empty response")
                return False
        except Exception as error:
            print(f"[ERROR] Model connection test failed: {str(error)}")
            return False

    def model_max_token(self, model_name: str) -> int:
        """Retrieves the pre-loaded maximum token limit for a given model."""
        config: ModelConfig | None = self.model_configs.get(model_name.upper())
        if not config:
            raise ValueError(f"Config for model '{model_name}' not found.")
        return config.max_tokens

    def model_max_chunk(self, model_name: str) -> int:
        """Retrieves the pre-loaded maximum chunk size for a given model."""
        config: ModelConfig | None = self.model_configs.get(model_name.upper())
        if not config:
            raise ValueError(f"Config for model '{model_name}' not found.")
        return config.max_chunk

    @staticmethod
    def count_tokens(content: str) -> int:
        """Counts the number of tokens in a string using Tiktoken."""
        try:
            encoding: Encoding = get_encoding("cl100k_base")
            return len(encoding.encode(content))
        except Exception:
            return len(content)  # Fallback to character count
