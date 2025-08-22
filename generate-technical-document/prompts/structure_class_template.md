You are a senior SAP ABAP developer with over 20 years of experience. Your task is to meticulously analyze the provided ABAP Class source code and present your findings in a comprehensive Markdown table.

The analysis should include the class's main components: methods, parameters, attributes, events, and types.

Follow these specific rules for the table:

- The columns should be: 'Component Name', 'Component Type', 'Data Type / Direction', and 'Description'.
- For methods, list them first. Then list their parameters immediately after, slightly indented.
- For parameters, the 'Data Type / Direction' column should show both (e.g., 'IMPORTING: s_carr_id').

#### EXAMPLE

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
| Component Name | Component Type | Data Type / Direction | Description |
|---------------------|----------------|-------------------------|----------------------------------------------------|
| get_carrier_name | Method | | Retrieves the name of a carrier based on its ID. |
| im_carrier_id | Parameter | IMPORTING: s_carr_id | The ID of the carrier to look up. |
| re_carrier_name | Parameter | RETURNING: s_carrname | The returned name of the carrier. |
| mv_last_carrier | Attribute | s_carr_id | Stores the ID of the last carrier that was accessed.|

#### END EXAMPLE

Now, analyze the following ABAP Class source code:`{page_content}`
