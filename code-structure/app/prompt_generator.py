"""
Generates tailored prompts for different types of ABAP objects.

This module contains the `PromptGenerator` class, which is responsible for
selecting and creating the most appropriate prompt for a given piece of ABAP
code based on its identified type (e.g., Class, Report, BDEF).
"""

from app.language_separator import ABAP
from langchain_core.documents.base import Document
from langchain_core.prompts import PromptTemplate
from textwrap import dedent
from typing import ClassVar, Dict, List, Self, Tuple


class PromptGenerator:
    """
    A singleton class that creates specific LLM prompts for ABAP code analysis.

    Based on the document type determined by the `Document_Splitter`, this class
    selects a corresponding detailed prompt template. These templates guide the
    LLM to produce structured and relevant analysis for different ABAP objects.
    """

    _instance: ClassVar[Self | None] = None

    def __new__(cls) -> Self:
        """Ensures that only one instance of PromptGenerator is created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initializes the PromptGenerator instance."""
        if not hasattr(self, "_initialized"):
            self._initialized: bool = True
            self._documents: Dict[str, Tuple[Document, PromptTemplate]] = {}
            self._document_type: List[str] = []

    def create_prompt(self, documents: Dict[str, List[Document]]) -> bool:
        """
        Creates and assigns a specific prompt for each document.

        It iterates through the documents, determines their category based on
        metadata, and assigns the appropriate `PromptTemplate`.

        Args:
            documents: A dictionary of documents from the `Document_Splitter`.

        Returns:
            True if prompts were successfully created, False otherwise.
        """
        for document_index, document_item in enumerate(documents.items(), 1):
            document_name, document_list = document_item
            print(f"Processing document {document_index}: {document_name}")
            if hasattr(document_list[0], "metadata") and document_list[0].metadata:
                document_type: str = document_list[0].metadata.get("document_type", "unknown")
                # Default to a generic category if the specific type is not found.
                assigned_category: str = "GENERIC"
                # Find the high-level category for the document type.
                for category, types_list in ABAP.get_document_categories().items():
                    if document_type in types_list:
                        assigned_category = category
                        break

                # Assign a prompt template based on the determined category.
                match assigned_category:
                    case "DATABASE":
                        self._documents[document_name] = (document_list[0], self._database_table_prompt())
                    case "OBJECT ORIENTED":
                        self._documents[document_name] = (document_list[0], self._class_prompt())
                    case "FUNCTION MODULE":
                        self._documents[document_name] = (document_list[0], self._function_module_prompt())
                    case "CLASSICAL":
                        self._documents[document_name] = (document_list[0], self._report_program_prompt())
                    case "RAP FRAMEWORK":
                        self._documents[document_name] = (document_list[0], self._behavior_definition_prompt())

        return True if self._documents else False

    @property
    def get_documents(self) -> Dict[str, Tuple[Document, PromptTemplate]]:
        """
        Returns the dictionary of documents paired with their generated prompts.
        """
        return self._documents

    @property
    def clear_documents(self) -> bool:
        """Clears the stored documents and prompts, resetting the instance."""
        self._documents.clear()
        self._initialized = False
        return True

    # --- Private methods to create PromptTemplate instances ---

    def _database_table_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["page_content"],
            template=self._database_table_template,
        )

    def _class_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["page_content"],
            template=self._class_template,
        )

    def _function_module_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["page_content"],
            template=self._function_module_template,
        )

    def _enhancement_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["page_content"],
            template=self._enhancement_template,
        )

    def _report_program_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["page_content"],
            template=self._report_program_template,
        )

    def _behavior_definition_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["page_content"],
            template=self._behavior_definition_template,
        )

    # --- Properties containing the detailed prompt templates ---

    @property
    def _database_table_template(self) -> str:
        """
        Returns the detailed instruction template for analyzing an ABAP database table.
        This prompt guides the LLM to produce a structured Markdown table as output.
        """
        return dedent("""
        You are a senior SAP ABAP developer with over 20 years of experience across the entire ABAP stack, including Core ABAP, ABAP on HANA, and modern ABAP DDL syntax.
        Your task is to meticulously analyze the provided ABAP Data Definition Language (DDL) source code for a database table and extract key details about each field.

        Present your analysis in a tabular format with the following columns: 'Field Name', 'Field Type', 'Is Key Field', and 'Description'.

        Follow these specific rules for each column:
        1.  **Field Name**: Extract the field's technical name exactly as it appears in the code.
        2.  **Field Type**: Extract the field's data type (e.g., mandt, /dmo/carrier_id).
        3.  **Is Key Field**: Determine if the field is part of the table's primary key. A field is a key if it is preceded by the `key` keyword. The value in this column must be 'Yes' or 'No'.
        4.  **Description**: Provide a concise, human-readable description for the field. You should infer its purpose from the field's name and type. For standard SAP fields (like mandt, client, created_by, last_changed_at), provide their standard meaning.

        If you encounter an `INCLUDE` statement, do not list the individual fields from the include. Instead, make a brief note below that the table contains an include structure, mentioning its name.

        ### EXAMPLE
        If you receive the following code:
        ```abap
        define table zmy_demo_table {{
          key client   : mandt not null;
          key demo_id  : sysuuid_c32 not null;
          created_at : timestampl;
          description: abap.string(100);
        }}
        ```
        Your output must be:
        | Field Name  | Field Type   | Is Key Field | Description                            |
        |-------------|--------------|--------------|----------------------------------------|
        | `client`    | `mandt`      | Yes          | The client key for the table.          |
        | `demo_id`   | `sysuuid_c32`| Yes          | The unique ID for the demo record.     |
        | `created_at`| `timestampl` | No           | The timestamp when the record was created. |
        | `description`|`abap.string(100)`|No| A description for the record. |
        ### END EXAMPLE

        Now, analyze the following ABAP DDL source code:
        {page_content}
        """)

    @property
    def _class_template(self) -> str:
        """
        Returns a detailed instruction template for analyzing an ABAP Class.
        This prompt guides the LLM to produce a structured Markdown table summarizing
        the class's components.
        """
        return dedent("""
        You are a senior SAP ABAP developer with over 20 years of experience. Your task is to meticulously analyze the provided ABAP Class source code and present your findings in a comprehensive Markdown table.

        The analysis should include the class's main components: methods, parameters, attributes, events, and types.

        Follow these specific rules for the table:
        -   The columns should be: 'Component Name', 'Component Type', 'Data Type / Direction', and 'Description'.
        -   For methods, list them first. Then list their parameters immediately after, slightly indented.
        -   For parameters, the 'Data Type / Direction' column should show both (e.g., 'IMPORTING: s_carr_id').

        ### EXAMPLE
        If you receive the following code:
        ```abap
        CLASS zcl_carrier_manager DEFINITION PUBLIC.
          PUBLIC SECTION.
            METHODS get_carrier_name
              IMPORTING
                im_carrier_id TYPE s_carr_id
              RETURNING
                VALUE(re_carrier_name) TYPE s_carrname.
          PRIVATE SECTION.
            DATA mv_last_carrier TYPE s_carr_id.
        ENDCLASS.
        ```

        Your output must be:
        | Component Name      | Component Type | Data Type / Direction   | Description                                        |
        |---------------------|----------------|-------------------------|----------------------------------------------------|
        | `get_carrier_name`  | **Method** |                         | Retrieves the name of a carrier based on its ID.   |
        | `im_carrier_id`     | Parameter      | `IMPORTING: s_carr_id`  | The ID of the carrier to look up.                  |
        | `re_carrier_name`   | Parameter      | `RETURNING: s_carrname` | The returned name of the carrier.                  |
        | `mv_last_carrier`   | **Attribute** | `s_carr_id`             | Stores the ID of the last carrier that was accessed.|
        ### END EXAMPLE

        Now, analyze the following ABAP Class source code:
        {page_content}
        """)

    @property
    def _function_module_template(self) -> str:
        """
        Returns a detailed instruction template for analyzing an ABAP Function Module.
        This prompt guides the LLM to summarize the FM's purpose and list its
        parameters and exceptions in a structured format.
        """
        return dedent("""
        You are an expert SAP ABAP developer specializing in procedural programming and function modules. Your task is to meticulously analyze the provided Function Module source code and present your findings in a comprehensive Markdown table.

        Your analysis must include a high-level summary and a detailed breakdown of all parameters and exceptions.

        Follow these specific rules for the table:
        - The columns should be: 'Parameter Name', 'Direction', 'Data Type', and 'Description'.
        - For each parameter, correctly identify its direction: `IMPORTING`, `EXPORTING`, `CHANGING`, `TABLES`, or `RETURNING`.
        - Also, list any `EXCEPTIONS` defined at the end of the analysis.

        ### EXAMPLE
        If you receive the following code:
        ```abap
        FUNCTION z_get_material_details
          IMPORTING
            VALUE(im_matnr) TYPE matnr
          EXPORTING
            VALUE(ex_material) TYPE mara
          EXCEPTIONS
            not_found.
        ENDFUNCTION.
        ```

        Your output must be:
        | Parameter Name | Direction | Data Type | Description                              |
        |----------------|-----------|-----------|------------------------------------------|
        | `im_matnr`     | IMPORTING | `matnr`   | The material number to be looked up.     |
        | `ex_material`  | EXPORTING | `mara`    | The returned material master record.     |

        **Exceptions:**
        - `not_found`: Raised if the material number does not exist in the database.
        ### END EXAMPLE

        Now, analyze the following ABAP Function Module source code:
        {page_content}
        """)

    @property
    def _enhancement_template(self) -> str:
        """
        Returns a detailed instruction template for analyzing ABAP enhancement
        implementations like BAdIs and Exits.
        """
        return dedent("""
        You are an expert SAP ABAP developer specializing in the Enhancement Framework. 
        Your task is to analyze the provided source code, which is part of a BAdI implementation or an enhancement exit, and explain its purpose.

        Your analysis must include:
        1.  An identification of the enhancement being implemented (e.g., BAdI name, Exit name).
        2.  A high-level summary of what the custom logic achieves.
        3.  A breakdown of the key logic, such as important method calls, data modifications, or checks being performed.

        Present your findings in a clear, readable format.

        ### EXAMPLE
        If you receive the following code, which is a method of a BAdI implementation class:
        ```abap
        METHOD if_ex_badi_name~my_method.
          " BAdI for Sales Order custom checks
          IF sy-tcode = 'VA01'.
            READ TABLE i_sales_items INTO DATA(ls_item) INDEX 1.
            IF ls_item-matnr = 'DUMMY_MATERIAL'.
              MESSAGE 'Dummy material is not allowed.' TYPE 'E'.
            ENDIF.
          ENDIF.
        ENDMETHOD.
        ```

        Your output must be:
        **Analysis for Enhancement Implementation**

        **Enhancement Point:** BAdI `BADI_NAME`, Method `MY_METHOD`.

        **Summary:** This enhancement implements a custom validation during sales order creation to prevent the use of a specific dummy material.

        **Key Logic Breakdown:**
        - The code specifically triggers during the sales order creation transaction (`VA01`).
        - It reads the first item from the sales order items table.
        - It checks if the material number for this item is `'DUMMY_MATERIAL'`.
        - If the condition is met, it raises an error message, stopping the process.
        ### END EXAMPLE

        Now, analyze the following ABAP enhancement source code:
        {page_content}
        """)

    @property
    def _report_program_template(self) -> str:
        """
        Returns a detailed instruction template for analyzing an ABAP Report Program.
        This prompt guides the LLM to identify the report's purpose, selection
        screen elements, and main processing blocks.
        """
        return dedent("""
        You are a senior SAP ABAP developer with deep experience in classical and modern report programming. Your task is to meticulously analyze the provided ABAP Report Program source code and present your findings.

        Your analysis must include a summary, a breakdown of the selection screen elements, and an overview of the main processing logic blocks.

        Follow these specific rules:
        - The columns for the selection screen table should be: 'Element Name', 'Type', 'Data Type', and 'Description'.
        - Identify `PARAMETERS` and `SELECT-OPTIONS`.
        - Describe the purpose of the main event blocks like `INITIALIZATION` and `START-OF-SELECTION`.

        ### EXAMPLE
        If you receive the following code:
        ```abap
        REPORT z_my_sales_report.

        PARAMETERS: p_bukrs TYPE bukrs OBLIGATORY.
        SELECT-OPTIONS: s_vbeln FOR vbak-vbeln.

        INITIALIZATION.
          p_bukrs = '1000'.

        START-OF-SELECTION.
          SELECT * FROM vbak INTO TABLE @DATA(lt_vbak)
            WHERE vbeln IN @s_vbeln.
          cl_demo_output=>display( lt_vbak ).
        ```

        Your output must be:
        **Report Program: `z_my_sales_report`**

        **Summary:** This report selects and displays sales document headers (`VBAK`) based on user-defined criteria for company code and sales document numbers.

        **Selection Screen Elements:**
        | Element Name | Type            | Data Type | Description                              |
        |--------------|-----------------|-----------|------------------------------------------|
        | `p_bukrs`    | Parameter       | `bukrs`   | A mandatory input for the Company Code.  |
        | `s_vbeln`    | Select-Option   | `vbak-vbeln`| Allows a range of Sales Document Numbers.|

        **Processing Logic:**
        - **INITIALIZATION:** Sets the default value for the company code parameter to '1000'.
        - **START-OF-SELECTION:** Selects data from the `VBAK` table based on the user's input in the `s_vbeln` select-option and displays the results.
        ### END EXAMPLE

        Now, analyze the following ABAP Report Program source code:
        {page_content}
        """)

    @property
    def _behavior_definition_template(self) -> str:
        """
        Returns a detailed instruction template for analyzing a RAP Behavior Definition.
        This prompt guides the LLM to break down the BDEF file, identifying the
        implementation class, entities, and their defined behaviors (operations,
        actions, determinations).
        """
        return dedent("""
        You are an expert SAP ABAP developer specializing in the ABAP RESTful Application Programming Model (RAP). 
        Your task is to meticulously analyze the provided ABAP RESTFul Application Programming Model source code and describe its structure.

        Follow these specific rules for the table:
        - The columns should be: 'Keyword', 'Entity / Alias', and 'Details / Description'.
        - Identify the implementation class, aliases, entity behaviors (standard operations), actions, determinations, and validations.

        ### EXAMPLE
        If you receive the following code:
        ```abap
        managed implementation in class zbp_i_travel_m unique;
        define behavior for Z_I_TRAVEL_M alias Travel
        {{
          create;
          update;
          delete;
          action acceptTravel result [1] $self;
          determination setStatusOnCreate on modify {{ create; }}
        }}
        ```
        Your output must be:
        | Keyword         | Entity / Alias | Details / Description                                               |
        |-----------------|----------------|---------------------------------------------------------------------|
        | `implementation`| -              | Implemented in class `zbp_i_travel_m`. The behavior is 'managed'.   |
        | `define behavior`| `Z_I_TRAVEL_M` | Defines the behavior for the root entity, using the alias `Travel`. |
        | `create`        | Travel         | Enables the standard Create operation for the Travel entity.        |
        | `update`        | Travel         | Enables the standard Update operation for the Travel entity.        |
        | `delete`        | Travel         | Enables the standard Delete operation for the Travel entity.        |
        | `action`        | `acceptTravel` | Defines a custom action that returns a single instance of the entity. |
        | `determination` | `setStatusOnCreate` | A determination that triggers on creation to set an initial status. |
        ### END EXAMPLE

        Now, analyze the following ABAP BDEF source code:
        {page_content}
        """)
