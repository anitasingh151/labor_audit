# Labor Audit Calculation Update Process

## Overview

When a new calculation needs to be added or an existing calculation needs to be modified, follow the steps below.

---

## Step 1: Update the Calculation Function in `labor.py`

Open the `labor.py` file.

* Locate the existing function that needs to be modified, or create a new function.
* Define all required input parameters.
* Implement the business logic according to the provided requirements.

Example:

```python
def projected_to_complete(projected_hours_at_complete,
                          jtd_hours,
                          tc_hours_excluded):
    jtd_total_hours = jtd_hours + tc_hours_excluded
    return projected_hours_at_complete - jtd_total_hours
```

Save the file after making the changes.

---

## Step 2: Register the Function in `labor_specs()`

Inside `labor.py`, locate the `labor_specs()` function.

Add or update the mapping between the calculated column and the corresponding Python function.

Example:

```python
"local_projected_hours_to_complete": lambda r: projected_to_complete(
    r["projected_hours_at_complete"],
    r["jtd_hours"],
    r["tc_hours_excluded"]
),
```

This mapping tells the system which function should be executed for each calculated column.

Save the file after making the changes.

---

## Step 3: Configure the Audit Comparison

Open `run_labor_audit.py`.

Locate the `possible_pairs` list.

Add or update the column mapping that compares the locally calculated value against the value from the source file.

Example:

```python
possible_pairs = [
    ("local_projected_hours_to_complete", "Projected_Hours_To_Complete"),
]
```

Where:

* First value = Locally calculated column name
* Second value = Source Excel column name to compare against

Save the file after making the changes.

---

## Step 4: Execute the Audit

After all updates are completed and files are saved, run the application:

```bash
python3 main.py yourfilename.xlsx
```

Example:

```bash
python3 main.py Labor_Audit_Input.xlsx
```

The system will:

1. Read the Excel file.
2. Execute all configured calculations.
3. Compare local results with source values.
4. Generate the audit output showing matches and mismatches.

---

## Summary

For every new calculation or logic change:

1. Update/Create the calculation function in `labor.py`.
2. Add the function mapping inside `labor_specs()`.
3. Add the comparison pair in `run_labor_audit.py`.
4. Save all files.
5. Run:

```bash
python3 main.py yourfilename.xlsx
```

6. Review the generated audit results.

