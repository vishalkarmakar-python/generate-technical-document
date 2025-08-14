# ABAP Code Documentation Generator

This Python application leverages local Large Language Models (LLMs) via Ollama to analyze ABAP source code. It automatically loads ABAP files, intelligently splits them into meaningful chunks, analyzes each chunk to understand its logic and purpose, and then generates a comprehensive and structured technical analysis in a clean Markdown format.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Workflow](#workflow)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [License](#license)

## Features

- **Automated Code Loading**: Recursively loads all `.abap` files from a specified directory.
- **Intelligent Code Splitting**: Splits large ABAP files into smaller, semantically coherent chunks using ABAP-specific separators.
- **AI-Powered Analysis**: Utilizes a local LLM via Ollama to analyze the functionality, logic, and purpose of each code chunk.
- **Structured Output**: Generates a structured analysis and summary for each code chunk, which can be parsed and validated.
- **Markdown Reports**: Creates detailed and easy-to-read Markdown reports for each analyzed file.

## Project Structure

```
.
├── app
│ ├── init.py
│ ├── create_document.py
│ ├── document_splitter.py
│ ├── generate_document.py
│ ├── language_model.py
│ ├── language_separator.py
│ ├── prompt_generator.py
│ └── structured_output.py
├── .env
├── .python-version
├── main.py
├── pyproject.toml
├── ruff.toml
└── README.md
```

## Workflow

1.  **Load Documents**: The application starts by loading all ABAP files from the user-provided directory.
2.  **Split Documents**: The loaded files are then split into smaller chunks, considering the ABAP code structure to maintain context.
3.  **Create Prompts**: For each code chunk, a specialized prompt is generated based on the detected ABAP object type (e.g., Class, Report, BDEF) to guide the LLM's analysis.
4.  **Analyze Chunks**: Each chunk is individually sent to a large language model for analysis. The model provides a detailed explanation and a summary of the code based on the tailored prompt.
5.  **Generate Report**: The analysis for each chunk is compiled into a single, well-formatted Markdown file for each original ABAP file.

## Prerequisites

- Python 3.13 or higher
- [Ollama](https://ollama.com/) installed and running with a downloaded model.
- [cite_start]Recommended LLM: `qwen2.5-coder:7b` (or any other suitable model configured in the `.env` file)[cite: 1].

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (optional but recommended):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    [cite_start]Dependencies are listed in the `pyproject.toml` file[cite: 2]. You can install them using a tool like `pip`.
    ```bash
    pip install langchain langchain-community langchain-core langchain-ollama pandas pydantic python-dotenv tiktoken tqdm transformers
    ```

## Configuration

1.  **Create a `.env` file** in the root directory of the project.
2.  [cite_start]**Add the following environment variables** to the `.env` file and customize them for your setup[cite: 1]:

    ```env
    # LLM Models
    OLLAMA_MODEL_QWEN="qwen2.5-coder:7b"
    OLLAMA_MODEL_QWEN_MAX_TOKENS=16384
    OLLAMA_MODEL_QWEN_MAX_CHUNK=16384

    # Add other models if needed, following the same pattern
    # OLLAMA_MODEL_GEMMA="gemma:7b"
    # OLLAMA_MODEL_GEMMA_MAX_TOKENS=8192
    # OLLAMA_MODEL_GEMMA_MAX_CHUNK=8192

    # LLM Configuration
    OLLAMA_MODEL_BASE_URL="http://localhost:11434"
    OLLAMA_MODEL_TEMPERATURE=0.1
    OLLAMA_GPU=8

    # Database connection details (if needed by your extensions)
    DATABASE_HOST="127.0.0.1"
    DATABASE_USER="postgres"
    DATABASE_PASSWORD="your_password"
    DATABASE_NAME="postgres"
    DATABASE_PORT="5432"
    ```

    [cite_start]Make sure the `OLLAMA_MODEL_...` variables match a model you have pulled with Ollama[cite: 1].

## Usage

1.  **Run the application from the root directory:**
    ```bash
    python main.py
    ```
2.  **Provide the required inputs** when prompted:
    - Path to the directory containing your ABAP source code files.
    - Path to the output directory where the analysis reports will be saved.
    - The name of the model to use for analysis (e.g., `QWEN`).
3.  The application will process the files and generate the analysis reports in the specified output directory.

## Dependencies

[cite_start]The main dependencies for this project are listed in the `pyproject.toml` file[cite: 2]. Key libraries include:

- [cite_start]`langchain` [cite: 2]
- [cite_start]`langchain-community` [cite: 2]
- [cite_start]`langchain-core` [cite: 2]
- [cite_start]`langchain-ollama` [cite: 2]
- [cite_start]`pydantic` [cite: 2]
- [cite_start]`python-dotenv` [cite: 2]

[cite_start]For a complete list of dependencies, please refer to the `[project]` section in the `pyproject.toml` file[cite: 2].

## License

This project is licensed under the MIT License.
