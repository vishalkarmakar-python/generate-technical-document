"""
Defines the Pydantic model for structured output from the language model.

This module provides a schema that helps ensure the LLM's responses are in a
predictable, structured format, making them easier to parse and use in the
final report.
"""

from pydantic import BaseModel, Field

# Field descriptions guide the LLM on what content to generate for each field.
_analysis: str = "A detailed, technical breakdown of the code chunk. Explain the logic, flow, and purpose of every code block."
_summary: str = "A high-level summary of the code chunk's overall purpose and functionality."


class Code_Analysis(BaseModel):
    """
    Defines the expected structure for the analysis of a single code chunk.
    The LLM is instructed to fill out these two fields based on its analysis.
    """

    analysis: str = Field(description=_analysis)
    summary: str = Field(description=_summary)


# This description string provides a template to the LLM for generating a
# Markdown table. It guides the model to produce output in the desired format.
_structure_description: str = "|Field Name|Field Type|Is Key Field|Description|\n|---|---|---|---|\n"


class Code_Structure(BaseModel):
    """
    Pydantic model for receiving structured analysis from the LLM.

    This class defines the expected structure of the LLM's output. By using
    Pydantic, we can automatically parse and validate the response. The `page_content`
    field is designed to capture the main analysis, often formatted as a
    Markdown table as guided by the `_description`.
    """

    page_content: str = Field(description=_structure_description)


_specification_description: str = "The full technical specification document in Markdown format."


class Technical_Specification(BaseModel):
    """
    Pydantic model for the technical specification.
    """

    page_content: str = Field(description=_specification_description)
