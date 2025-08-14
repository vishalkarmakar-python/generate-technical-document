"""
Manages the connection and interaction with the Ollama language model.

This module provides a singleton wrapper class `Ollama` for the LangChain
`ChatOllama` instance. It handles loading configuration from environment
variables, initializing the model, testing the connection, and providing
helper utilities like token counting.
"""

from contextlib import contextmanager
from dotenv import load_dotenv
from langchain_core.messages.base import BaseMessage
from langchain_ollama import ChatOllama
from os import getenv
from tiktoken import Encoding, get_encoding
from typing import Any, ClassVar, Dict, Generator, List, Literal, Self


class Ollama:
    """
    A singleton class to manage and provide access to a ChatOllama instance.

    Responsibilities:
    - Loading model configuration from a .env file.
    - Initializing the ChatOllama model with the correct parameters.
    - Verifying the connection to the Ollama server.
    - Providing a single, shared instance of the LLM across the application.
    - Offering utility methods for token counting and context management.
    """

    _instance: ClassVar[Self | None] = None
    _model_name: ClassVar[str | None] = None  # Track which model was initialized

    def __new__(cls) -> Self:
        """Ensures that only one instance of Ollama is created."""
        if cls._instance is None:
            cls._instance = super(Ollama, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the Ollama instance.

        The `_initialized` flag prevents the heavy initialization logic from
        running more than once.
        """
        if not hasattr(self, "_initialized"):
            self._initialized: bool = False
            self._is_connected: bool = False
            self._llm: ChatOllama

    def initialize_llm(self, model_name: str) -> bool:
        """
        Loads configuration, creates, and tests the ChatOllama instance.

        This is the main setup method. It ensures all necessary environment
        variables are present, creates the LLM instance, and performs a
        connection test.

        Args:
            model_name: The name of the model to initialize (e.g., "QWEN").

        Returns:
            True if initialization is successful, False otherwise.

        Raises:
            RuntimeError: If configuration is missing or initialization fails.
        """
        try:
            # Load and validate environment variables from the .env file.
            if self._load_environment_variables(model_name=model_name):
                # Create the LangChain ChatOllama instance.
                self._llm = self._create_llm_instance(model_name=model_name)
                # Verify that the application can communicate with the LLM server.
                self._is_connected = self._test_connection()
                # Mark as successfully initialized.
                self._initialized = True
                return True
            else:
                raise RuntimeError("Failed to load required environment variables")

        except Exception as error:
            print(f"[ERROR] Ollama initialization failed: {str(error)}")
            raise

    def get_llm_model(self) -> ChatOllama:
        """
        Provides access to the initialized ChatOllama model instance.

        Returns:
            The initialized ChatOllama instance.

        Raises:
            Exception: If the LLM has not been initialized.
        """
        if not self._initialized or not hasattr(self, "_llm"):
            raise Exception("LLM not initialized. Call initialize_llm() first.")
        return self._llm

    def destroy_llm(self) -> None:
        """
        Cleans up the LLM instance and resets the initialization state.
        """
        if self._initialized and hasattr(self, "_llm"):
            print("[INFO] Destroying Ollama instance...")
            del self._llm
            self._initialized = False
            self._is_connected = False

    def _load_environment_variables(self, model_name: str) -> bool:
        """
        Loads required environment variables from a .env file into a config dict.

        Args:
            model_name: The specific model for which to load variables.

        Returns:
            True if all required variables are loaded and parsed successfully.

        Raises:
            Exception: If the .env file cannot be loaded or a required
                       variable is missing.
        """
        self._config: Dict[str, Any] = {}
        # Define the expected environment variable keys based on the model name.
        required_vars: List[str] = [
            f"OLLAMA_MODEL_{model_name}",
            f"OLLAMA_MODEL_{model_name}_MAX_TOKENS",
            f"OLLAMA_MODEL_{model_name}_MAX_CHUNK",
            "OLLAMA_MODEL_BASE_URL",
            "OLLAMA_MODEL_TEMPERATURE",
            "OLLAMA_GPU",
        ]

        if load_dotenv():  # Load variables from .env file.
            for var in required_vars:
                value: str | None = getenv(key=var)
                if value is None:
                    raise Exception(f"Missing required environment variable: {var}")
                self._config[var] = value

            # Validate and convert specific variables to their correct types.
            self._config[f"OLLAMA_MODEL_{model_name}_MAX_TOKENS"] = int(self._config[f"OLLAMA_MODEL_{model_name}_MAX_TOKENS"])
            self._config[f"OLLAMA_MODEL_{model_name}_MAX_CHUNK"] = int(self._config[f"OLLAMA_MODEL_{model_name}_MAX_CHUNK"])
            self._config["OLLAMA_GPU"] = int(self._config["OLLAMA_GPU"])
            self._config["OLLAMA_MODEL_TEMPERATURE"] = float(self._config["OLLAMA_MODEL_TEMPERATURE"])
            return True
        else:
            raise Exception("Environment variable loading failed: .env file not found.")

    def _create_llm_instance(self, model_name: str) -> ChatOllama:
        """
        Creates an instance of the ChatOllama model with loaded configuration.

        Args:
            model_name: The name of the model to instantiate.

        Returns:
            A configured instance of `ChatOllama`.

        Raises:
            Exception: If the instance creation fails.
        """
        try:
            llm_instance = ChatOllama(
                model=self._config[f"OLLAMA_MODEL_{model_name}"],
                base_url=self._config["OLLAMA_MODEL_BASE_URL"],
                temperature=self._config["OLLAMA_MODEL_TEMPERATURE"],
                num_ctx=self._config[f"OLLAMA_MODEL_{model_name}_MAX_TOKENS"],
                num_gpu=self._config["OLLAMA_GPU"],
                num_predict=self._config[f"OLLAMA_MODEL_{model_name}_MAX_TOKENS"],
                top_k=2,
                top_p=0.5,
            )
            return llm_instance
        except Exception as error:
            print(f"[ERROR] Failed to create ChatOllama instance: {error}")
            raise

    def _test_connection(self) -> bool:
        """
        Sends a simple test message to the LLM to verify the connection.

        Returns:
            True if the connection is successful, False otherwise.
        """
        assert self._llm is not None, "Ollama model is not initialized"
        try:
            test_message: str = "Hello, this is a connection test. Respond with a single word."
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

    @contextmanager
    def get_llm(self) -> Generator[ChatOllama, None, None]:
        """
        A context manager to safely use the LLM instance.

        Yields:
            The ChatOllama instance.

        Raises:
            Exception: If the LLM is not initialized or if an error occurs
                       during its operation.
        """
        if not self._initialized or not hasattr(self, "_llm"):
            raise Exception("LLM not initialized. Check initialization status.")
        try:
            yield self._llm
        except Exception as error:
            print(f"[ERROR] LLM operation error: {str(error)}")
            raise

    def __enter__(self) -> Self:
        """Allows the instance to be used as a context manager."""
        if not self._initialized:
            raise Exception("LLM not initialized. Check initialization status.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Handles exiting the context, reporting any exceptions."""
        if exc_type is not None:
            print(f"[ERROR] Exception occurred in Ollama context: {exc_type.__name__}: {exc_val}")
        return None

    def __del__(self) -> None:
        """Destructor to log when the instance is garbage collected."""
        try:
            if hasattr(self, "_model"):
                print(f"[DEBUG] Ollama instance for model '{self._model_name}' is being garbage collected")
        except:
            pass

    @staticmethod
    def count_tokens(content: str) -> int:
        """
        Counts the number of tokens in a string using Tiktoken.

        Args:
            content: The string to count tokens for.

        Returns:
            The number of tokens. Falls back to character count on error.
        """
        try:
            encoding: Encoding = get_encoding("cl100k_base")
            return len(encoding.encode(content))
        except Exception as error:
            print(f"[ERROR] Tiktoken counting failed: {error}")
            return len(content)

    @staticmethod
    def model_max_token(model_name: str) -> int:
        """
        Retrieves the maximum token limit for a given model from env variables.

        Args:
            model_name: The name of the model.

        Returns:
            The integer value of the maximum token limit.

        Raises:
            ValueError: If the corresponding environment variable is not set.
        """
        var_name: str = f"OLLAMA_MODEL_{model_name}_MAX_TOKENS"
        max_token: str | None = None
        if load_dotenv() and (max_token := getenv(var_name)) is not None:
            return int(max_token)
        else:
            raise ValueError(f"Required environment variable '{var_name}' is not set.")

    @property
    def is_initialized(self) -> bool:
        """Returns True if the LLM instance has been initialized."""
        return getattr(self, "_initialized", False)

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the instance."""
        status: Literal["initialized", "not initialized"] = "initialized" if self.is_initialized else "not initialized"
        model: str = self._model_name or "unknown"
        return f"Ollama(model='{model}', status='{status}')"
