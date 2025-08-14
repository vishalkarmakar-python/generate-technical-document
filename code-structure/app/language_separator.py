"""
Contains ABAP language-specific constants and configurations.

This module provides a central, non-instantiable class `ABAP` that serves as a
namespace for holding data used across the application for parsing and
categorizing ABAP code. This includes keywords for object type identification,
high-level categories for prompt selection, and separators for text splitting.
"""

from typing import Dict, List


class ABAP:
    """
    A container for ABAP-specific constants.

    This class is not meant to be instantiated. It provides class-level methods
    to access dictionaries of keywords and categories, and a list of separators
    used for intelligently splitting ABAP code.
    """

    # A mapping of ABAP object types to a list of keywords that commonly appear in them.
    # This is used by `Document_Splitter` to guess the type of a given code file.
    _DOCUMENT_KEYWORDS: Dict[str, List[str]] = {
        # === Database Objects & CDS Views ===
        "DATABASE TABLE": [
            "tableCategory",
            "deliveryClass",
            "dataMaintenance",
            "define",
            "table",
            "key",
            "include",
        ],
        "STRUCTURE": [
            "define",
            "structure",
            "key",
            "include",
        ],
        # === ABAP RESTful Application Programming Model (RAP) ===
        "PROJECTION ENTITY": [
            "define",
            "root",
            "view",
            "entity",
            "provider",
            "contract",
            "transactional_query",
            "projection",
        ],
        "ROOT ENTITY": [
            "define",
            "root",
            "view",
            "entity",
            "select",
            "from",
            "join",
        ],
        "ENTITY": [
            "define",
            "view",
            "entity",
            "select",
            "from",
            "join",
        ],
        "VALUE HELP ENTITY": [
            "objectmodel",
            "datacategory",
            "#value_help",
            "servicequality",
            "define",
            "view",
            "entity",
            "select",
            "from",
            "join",
        ],
        "METADATA ENTITY": [
            "metadata",
            "layer",
            "annotate",
            "withentity",
        ],
        "ABSTRACT ENTITY": [
            "define",
            "abstract",
            "entity",
        ],
        "CUSTOM ENTITY": [
            "define",
            "custom",
            "entity",
        ],
        "SERVICE DEFINITION": [
            "define",
            "service",
            "expose",
        ],
        "BEHAVIOR PROJECTION": [
            "projection",
            "strict",
            "define",
            "behavior",
            "use",
            "create",
            "update",
            "delete",
            "action",
            "determination",
            "validation",
        ],
        "UNMANAGED BEHAVIOR DEFINITION": [
            "unmanaged",
            "implementation",
            "class",
            "define",
            "behavior",
            "for",
        ],
        "MANAGED BEHAVIOR DEFINITION": [
            "managed",
            "implementation",
            "class",
            "define",
            "behavior",
            "for",
        ],
        # === Object-Oriented Programming ===
        "CLASS": [
            "class",
            "definition",
            "create",
            "interfaces",
            "public",
            "protected",
            "private",
            "final",
            "section",
            "class-methods",
            "methods",
            "implementation",
        ],
        # === Classical ABAP ===
        "REPORT PROGRAM": [
            "report",
            "selection-screen",
            "parameters",
            "select-options",
            "initialization",
            "at selection-screen",
            "start-of-selection",
            "end-of-selection",
            "top-of-page",
            "end-of-page",
            "perform",
            "form",
            "endform",
        ],
        # === Program Components ===
        "INCLUDE PROGRAM": [
            "perform",
            "form",
            "endform",
        ],
        # === Function Modules & Exits ===
        "FUNCTION MODULE": [
            "function",
            "importing",
            "exporting",
            "changing",
            "tables",
            "exceptions",
            "value",
            "optional",
            "endfunction",
        ],
        "EXITS": [
            "call",
            "user_exit",
            "customer",
            "function",
            "importing",
            "exporting",
            "changing",
            "tables",
            "exceptions",
            "value",
            "optional",
            "endfunction",
        ],
        # === Other Dictionary Objects ===
        "LOCK OBJECT": [
            "table",
            "lock mode",
            "lock",
            "unlock",
            "lock parameters",
        ],
        "NUMBER RANGE": [
            "number length domain",
            "number range number",
            "number range status",
        ],
    }

    # High-level categorization of document types. This simplifies the process
    # of selecting the correct prompt in `PromptGenerator`.
    _DOCUMENT_CATEGORIES: Dict[str, List[str]] = {
        "DATABASE": [
            "DATABASE TABLE",
            "STRUCTURE",
            "PROJECTION ENTITY",
            "ROOT ENTITY",
            "ENTITY",
            "VALUE HELP ENTITY",
            "METADATA ENTITY",
            "ABSTRACT ENTITY",
            "CUSTOM ENTITY",
            "LOCK OBJECT",
        ],
        "FUNCTION MODULE": [
            "FUNCTION MODULE",
            "EXITS",
        ],
        "OBJECT ORIENTED": [
            "CLASS",
        ],
        "RAP FRAMEWORK": [
            "SERVICE DEFINITION",
            "BEHAVIOR PROJECTION",
            "UNMANAGED BEHAVIOR DEFINITION",
            "MANAGED BEHAVIOR DEFINITION",
        ],
        "CLASSICAL": [
            "REPORT PROGRAM",
            "INCLUDE PROGRAM",
        ],
        "OTHER": [
            "NUMBER RANGE",
        ],
    }

    # A list of ABAP keywords used as separators for `RecursiveCharacterTextSplitter`.
    # These represent logical boundaries in the code, allowing for more coherent chunks.
    _SEPARATOR: List[str] = [
        # === RAP Objects & CDS Definitions ===
        "\nDEFINE ROOT VIEW ENTITY",
        "\nDEFINE VIEW ENTITY",
        "\nDEFINE ABSTRACT ENTITY",
        "\nDEFINE CUSTOM ENTITY",
        "\nDEFINE VIEW",
        "\nDEFINE TABLE FUNCTION",
        "\nANNOTATE ENTITY",
        "\nDEFINE ACCESS CONTROL",
        "\nDEFINE SERVICE",
        "\nUNMANAGED IMPLEMENTATION IN CLASS",
        "\nMANAGED IMPLEMENTATION IN CLASS",
        "\nDEFINE BEHAVIOR FOR",
        # === Class, Method & Interface Definitions ===
        "\nCLASS ",
        "\nENDCLASS.",
        "\nMETHOD ",
        "\nENDMETHOD.",
        "\nPUBLIC SECTION.",
        "\nPROTECTED SECTION.",
        "\nPRIVATE SECTION.",
        "\nINTERFACE ",
        "\nENDINTERFACE.",
    ]

    @classmethod
    def get_document_keywords(cls) -> Dict[str, List[str]]:
        """Returns a copy of the dictionary mapping ABAP object types to keywords."""
        return cls._DOCUMENT_KEYWORDS.copy()

    @classmethod
    def get_document_categories(cls) -> Dict[str, List[str]]:
        """Returns a copy of the dictionary mapping high-level categories to specific document types."""
        return cls._DOCUMENT_CATEGORIES.copy()

    @classmethod
    def get_separators(cls) -> List[str]:
        """Returns a copy of the list of separators for code splitting."""
        return cls._SEPARATOR.copy()
