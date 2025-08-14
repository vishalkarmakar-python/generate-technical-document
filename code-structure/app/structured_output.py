"""
Defines the Pydantic model for structured output from the language model.

This module provides a schema that helps ensure the LLM's responses are in a
predictable, structured format, making them easier to parse and use in the
final report.
"""

from pydantic import BaseModel, Field

# This description string provides a template to the LLM for generating a
# Markdown table. It guides the model to produce output in the desired format.
_description: str = "|Field Name|Field Type|Is Key Field|Description|\n|---|---|---|---|\n"
# _description: str = "content as per the prompt schema" # Alternative description


class Analysis(BaseModel):
    """
    Pydantic model for receiving structured analysis from the LLM.

    This class defines the expected structure of the LLM's output. By using
    Pydantic, we can automatically parse and validate the response. The `page_content`
    field is designed to capture the main analysis, often formatted as a
    Markdown table as guided by the `_description`.
    """

    page_content: str = Field(description=_description)
