
# Labor Audit Starter (v3.1) 

## Setup venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Setup pipenv (From installing the pipenv)
```bash
python3 -m pip install --user pipenv 
pipenv shell
pipenv install -r requirements.txt
exit
```

## Run labor analysis or cost analysis
- For Running labor analysis 'YourFile.xlsx' must be in the data/input directory.

```bash
python main.py YourFile.xlsx
```

### Auto-detect Run Description

When you run the following command:

```bash
python main.py YourFile.xlsx
```


The script searches for the Excel file `YourFile.xlsx` in the `data/input/{Company_Code_Date_Time}` directory, processes it, and generates a new file named `labor_mismatches.xlsx` in the `data` directory. 

The output file includes newly added columns (starts with prefix 'local_'), that highlight labor mismatches and other relevant audit details.

New Directory formed in data with Date and time stamp in name, it generates seperated calculated fields with relevant column names.

### Directory Structure

```graphql
RAY_CODE/
│
├── labor_audit/
│   ├── labor.py               # Core logic for generating new columns and mapping rules
│   ├── run_labor_audit.py     # Main audit runner — handles normalization and comparison
│   ├── formulas.py                # Contains comparison and difference calculation formulas
│
├── data/
│   ├── input/check_sheet.ipynb             # Place test Excel sheets here (any filename)
│                              
│
├── notebook/                  # Jupyter notebooks for testing column names, dtypes, etc.
│
└── main.py                    # Entry point to run the audit

launch.json                     #  Debuger settings for project.

```

### ⚙️ How It Works

1. Input Detection
    - The program automatically reads any Excel file placed in data/input/.

2. Field Generation
    - labor.py creates and maps new columns such as calculated hours, costs, etc.

3. Normalization & Comparison
    - run_labor_audit.py normalizes column data, applies formulas, and generates __match / __diff columns using formulas.py.

4. Output Generation
    - The result Excels is saved in the data/(Ex: "MLS_20251008_121609") and must have "labor_mismatches.xlsx" excel.



## Explicit modes + subtract columns -- Working
```bash
python run_labor_audit.py Book7.xlsx   --tc included --tc-subtract-col tc_hours_included   --unposted included --unposted-subtract-col additional_quantity
```

This version introduces:
- `unposted_value_eff` as the numeric unposted quantity to use across formulas.
- Formulas updated to reference `unposted_value_eff` (no more KeyError on 'unposted_quantity').

