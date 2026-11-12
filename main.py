import argparse
import os
import sys
import pandas as pd

from labor_audit import run_labor_audit
from utils.utils import print_column_types


INPUT_DIR = "data/input"
OUTPUT_DIR = "data"

def convert_floats_to_int(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert all float columns to Int64 safely (including newly created columns).
    Keeps NaN values intact.
    """
    float_cols = df.select_dtypes(include=["float"]).columns
    for col in float_cols:
        df[col] = df[col].round(0).astype("Int64", errors="ignore")
    return df

def generate_output_dir(df: pd.DataFrame) -> str:
    """
    Generate an output directory name from the first row's company identity
    alone (no timestamp) so re-running against the same company reuses the
    same folder and overwrites its files, instead of accumulating a new
    timestamped folder on every run.
    Priority:
        1. company_code (if exists)
        2. cost_type (if exists)
    """
    prefix = None
    if "Company Code" in df.columns and pd.notna(df.iloc[1]["Company Code"]):
        prefix = str(df.iloc[1]["Company Code"]).strip()
    elif "Cost Type" in df.columns and pd.notna(df.iloc[1]["Cost Type"]):
        prefix = str(df.iloc[1]["Cost Type"]).strip()

    folder_name = prefix if prefix else "output"

    output_dir = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

if __name__ == "__main__":

    p = argparse.ArgumentParser(description="Run Labor or Cost audit on an Excel file.")
    p.add_argument("input", help="Path to input Excel (.xlsx)")
    p.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Path to output Excel (.xlsx). Defaults to labor_mismatches.xlsx or cost_mismatches.xlsx",
    )
    p.add_argument("--tc", dest="tc_mode", choices=["included", "excluded"])
    p.add_argument("--unposted", dest="qty_mode", choices=["included", "excluded"])
    p.add_argument("--tc-subtract-col", dest="tc_subtract_col")
    p.add_argument("--unposted-subtract-col", dest="unposted_subtract_col")
    p.add_argument("--allow-missing", action="store_true")
    p.add_argument("--list-columns", action="store_true")
    p.add_argument("--add-columns", type=str, default="")
    p.add_argument("--column-types", action="store_true", help="Show data types of final output columns")

    args = p.parse_args()

    args.input = os.path.join(INPUT_DIR, args.input)
    df = pd.read_excel(args.input)
    # print("==========================================")
    # print("df",df.dtypes)

    if args.column_types:
        print_column_types(df)
        sys.exit(0)


    # Generate output directory based on first row
    output_dir = generate_output_dir(df)
  

    # Default output filename
    output_filename = "labor_mismatches333.xlsx"
    args.output = os.path.join(output_dir, output_filename)

    print(f"🔎 Running Labor Audit for file: {args.input}")
    print(f"📁 Output directory created: {output_dir}")

    audit_func = run_labor_audit.main
    print("argsargs",args)
    print("=======================")
    audit_func(args)
