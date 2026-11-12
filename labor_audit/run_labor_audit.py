import argparse
import json
from pathlib import Path
import numpy as np
import re
import pandas as pd
from config import TOLERANCE
from labor_audit.labor import labor_specs
from labor_audit.formulas import apply_formulae, compare_columns, convert_floats_to_int
from utils.utils import clean_headers, ensure_columns, ensure_compare_columns, normalize_inclusions


# string_based_json Path
_DUMMY_JSON_PATH = Path(__file__).resolve().parent / "dummylist.json"

# list_based_json Path
# _DUMMY_JSON_PATH = Path(__file__).resolve().parent / "dummylist.json"



def convert_all_floats_with_two_decimal(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["float"]).columns:
        # 1. Fill NaN with 0
        df[col] = df[col].fillna(0)
        df[col] = df[col].round(2)
    
    return df


def _apply_json_field_mapping(df: pd.DataFrame, path: Path = _DUMMY_JSON_PATH) -> pd.DataFrame:
    """
    Enrich DataFrame fields based on JSON mappings.
    """
    try:
        raw = json.loads(path.read_text())
    except FileNotFoundError:
        print(f"[WARN] JSON config missing at {path}; skipping enrichment.")
        return df
    except json.JSONDecodeError as exc:
        print(f"[WARN] Could not parse JSON config {path}: {exc}")
        return df

    data = raw.get("data", [])

    # Prepare target columns
    for col in ["company_id", "project_threshold", "jtd_actual_dollars", "jtd_cost"]:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = df[col].fillna(0)

    def normalize_to_list(value):
        """Normalize JSON field into a list of uppercase strings."""
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v).strip().upper() for v in value]
        if isinstance(value, str):
            return [v.strip().upper() for v in re.split(r"[,\s]+", value) if v.strip()]
        return [str(value).strip().upper()]

    # Apply row-by-row enrichment
    for i, row in df.iterrows():
        comp = str(row.get("company_code", "")).strip().upper()
        ctype = str(row.get("cost_type", "")).strip().upper()

        matched = False
        for entry in data:
            # Match by company_code
            company_codes = normalize_to_list(entry.get("company_code"))
            if comp and comp in company_codes:
                df.at[i, "company_id"] = entry.get("company_id", 0)
                df.at[i, "project_threshold"] = entry.get("project_threshold", 0)
                matched = True

            # Match by cost_type
            cost_types = normalize_to_list(entry.get("cost_type"))
            if ctype and ctype in cost_types:
                df.at[i, "jtd_actual_dollars"] = entry.get("jtd_actual_dollars", 0)
                df.at[i, "jtd_cost"] = entry.get("jtd_cost", 0)
                matched = True

        # If nothing matched, keep row defaults as 0
        if not matched:
            df.at[i, "company_id"] = df.at[i, "company_id"] or 0
            df.at[i, "project_threshold"] = df.at[i, "project_threshold"] or 0
            df.at[i, "jtd_actual_dollars"] = df.at[i, "jtd_actual_dollars"] or 0
            df.at[i, "jtd_cost"] = df.at[i, "jtd_cost"] or 0

    return df

def main(args):
    df = pd.read_excel(args.input)
    df.columns = clean_headers(df.columns)
    extra_cols = [c.strip() for c in args.add_columns.split(",") if c.strip()]
    df = ensure_columns(df, strict=not args.allow_missing, extra_columns=extra_cols)
  
  
    df = normalize_inclusions(
        df,
        tc_mode=args.tc_mode,
        qty_mode=args.qty_mode,
        tc_subtract_col=args.tc_subtract_col,
        unposted_subtract_col=args.unposted_subtract_col,
        strict=not args.allow_missing
    )

    # 🔄 Apply JSON-based enrichment for company_code & cost_type matches
    df = _apply_json_field_mapping(df)
 

    possible_pairs = [
        ("local_percent_of_quantity",        "percent_of_quantity"),
        ("local_earned_hours",               "earned_hours"),
        ("local_actual_over_earned",         "actual_/_earned"),
        ("local_earned_hours_over_under",    "earned_hours_over_(under)"),
        ("local_projected_hours_at_complete","projected_at_complete"),
        
        ("local_projected_hours_over_under", "projected_hours_over_(under)"),
        ("local_percent_of_estimate",        "percent_of_estimate"),
        ("local_estimated_production",       "estimated_production"),
        ("local_jtd_production",             "jtd_production"),
        ("local_estimated_hours_remaining",  "estimated_hours_remaining"),
        
        ("local_projected_hours_to_complete","projected_to_complete"),

        # ----------- new Changes [29th May2026]-----------------------
        ("local_projected_h_to_complete","projected_to_complete"),
        ("local_jtd_production_new",             "jtd_production"),
        
        # ------- Rules for the cost audit formulas------------------
        
        ("local_estimated_cost_per_hour", "percent_of_estimated_cost"),        
    ]

    specs = labor_specs()
    df_calc = apply_formulae(df, specs)

    COMPARE_PAIRS = []
    for local_col, remote_col in possible_pairs:
        if local_col in df_calc.columns and remote_col in df_calc.columns:
            COMPARE_PAIRS.append((local_col, remote_col))

    print("[DEBUG] Final COMPARE_PAIRS:", COMPARE_PAIRS)

    

    ensure_compare_columns(df, COMPARE_PAIRS, strict=not args.allow_missing)
    df_cmp  = compare_columns(df_calc, COMPARE_PAIRS, tolerance=TOLERANCE)

    print("\n\n[DEBUG] After Compared columns:", list(df_cmp.columns))

    # Identify mismatch rows across all match columns
    match_cols = [f"{a}__match" for a, _ in COMPARE_PAIRS if f"{a}__match" in df_cmp.columns]

    print("\n[DEBUG] Match columns:", match_cols)

    if not match_cols:
        print("\n[RAISE] No match columns found.")
        print("[DEBUG] COMPARE_PAIRS tested:", COMPARE_PAIRS)
        print("[DEBUG] Available df_cmp columns:", list(df_cmp.columns))
        raise ValueError("No match columns found — check COMPARE_PAIRS and your remote column names.")


    # Consider any NaN in match columns as NOT a match
    row_all_match = df_cmp[match_cols].fillna(False).all(axis=1)
    mismatches = df_cmp.loc[~row_all_match].copy()

    print("\n[SUMMARY]")
    for col in match_cols:
        vc = df_cmp[col].value_counts(dropna=False)
        print(f"{col}: {vc.to_dict()}")
    print(f"Rows total: {len(df_cmp)}, mismatches: {len(mismatches)}")
    
    mismatches = convert_all_floats_with_two_decimal(mismatches)
    mismatches.to_excel(args.output, index=False)
    print(f"✅ Labor audit complete. {len(mismatches)} mismatches saved to {args.output}")

    # Export each focused sheet safely
    for sheet_name, col_list in FOCUSED_SHEETS.items():
        available_cols = [c for c in col_list if c in df_cmp.columns]
        if not available_cols:
            print(f"[WARN] Columns for '{sheet_name}' not found — skipped.")
            continue

        focused_df = df_cmp[available_cols].copy()

        # Fill missing columns (so Excel always shows all expected ones)
        for col in col_list:
            if col not in focused_df.columns:
                focused_df[col] = pd.NA

        # Reorder to preserve your defined order
        focused_df = focused_df[col_list]

        focused_path = args.output.replace(".xlsx", f"_{sheet_name}.xlsx")
        focused_df.to_excel(focused_path, index=False)
        print(f"📊 Focused sheet '{sheet_name}' saved to {focused_path}")

    
# Define sets of focused exports
FOCUSED_SHEETS = {

        "local_percent_of_quantity":[
            "job_num_&_name",
            "job_number",
            "estimated_quantity",
            "jtd_quantity",
            "unposted_quantity_excluded",
            "local_percent_of_quantity",
            "local_percent_of_quantity__match",
            "local_percent_of_quantity__diff"
        ],

        
        "local_earned_hours": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "estimated_hours",
            "labor_percent_complete",
            "earned_hours",
            "local_earned_hours",
            "local_earned_hours__diff",
            "local_earned_hours__match",
        ],

        "local_actual_over_earned": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "jtd_hours",
            "jtd_hours_eff",
            "local_earned_hours",
            "actual_/_earned",
            "local_actual_over_earned",
            "local_actual_over_earned__diff",
            "local_actual_over_earned__match",
        ],

        

        "local_projected_hours_at_complete":[
            "job_num_&_name",
            "job_number",
            "cost_type",
            "labor_percent_complete",
            "estimated_hours",
            "jtd_hours",
            "projected_at_complete",
            "local_projected_hours_at_complete",
            "local_projected_hours_at_complete__diff",
            "local_projected_hours_at_complete__match"
        ],
        
        "local_earned_hours_over_under" : [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "labor_percent_complete",
            "jtd_hours",
            "earned_hours",
            "earned_hours_over_(under)",
            "local_earned_hours_over_under",
            "local_earned_hours_over_under__diff",
            "local_earned_hours_over_under__match"
        ],

        "local_projected_hours_over_under" :  [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "earned_hours",
            "jtd_hours",
            "projected_hours_over_(under)",
            "local_projected_hours_over_under",
            "local_projected_hours_over_under__diff",
            "local_projected_hours_over_under__match"
        ],

        "local_percent_of_estimate": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "estimated_hours",
            "jtd_hours",
            "tc_hours_excluded",
            "percent_of_estimate",
            "local_percent_of_estimate",
            "local_percent_of_estimate__diff",
            "local_percent_of_estimate__match",
        ],

        "local_jtd_production": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "estimated_quantity",
            "estimated_hours",
            "jtd_quantity",
            "unposted_quantity_excluded",
            "jtd_hours",
            "tc_hours_excluded",
            "jtd_production",
            "local_jtd_production",
            "local_estimated_production__diff",
            "local_estimated_production__match",
        ],

        "local_estimated_hours_remaining": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "estimated_hours",
            "tc_hours_excluded",
            "jtd_hours",
            "estimated_hours_remaining",
            "local_estimated_hours_remaining",
            "local_estimated_hours_remaining__diff",
            "local_estimated_hours_remaining__match",
        ],

        "local_estimated_production": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "estimated_hours",
            "estimated_quantity",
            "estimated_production",
            "local_estimated_production",
            "local_estimated_production__diff",
            "local_estimated_production__match"
        ],


        "local_projected_hours_to_complete": [
            "job_num_&_name",
            "job_number",
            "cost_type",
            "tc_hours_excluded",
            "jtd_hours",
            "local_projected_hours_at_complete",
            "projected_to_complete",
            "local_projected_hours_to_complete",
            "local_projected_hours_to_complete__diff",
            "local_projected_hours_to_complete__match"
        ],


        # ------- Rules for the cost audit formulas------------------
        
        "local_estimated_cost_per_hour": [
            "phase_description",
            "chart",
            "cost_type",
            "estimated_hours",
            "current_estimated_cost",
            "percent_of_estimated_cost",
            "local_estimated_cost_per_hour",
            "local_estimated_cost_per_hour__diff",
            "local_estimated_cost_per_hour__match"
        ],

        "local_variance_cost_per_hour": [
            "phase_description",
            "chart",
            "cost_type",
            "projected_cost_jsf",
            "current_estimated_cost",
            "variance_cost_per_hour"
        ],

        "local_percent_of_cost":[
            "phase_description",
            "chart",
            "jtd_actual_cost",
            "current_estimated_cost",
            "local_percent_of_cost"
        ],

        "local_actual_cost_per_hour":[
            "phase_description",
            "chart",
            "jtd_hours",
            "jtd_actual_dollars",
            "estimated_hours",
            "local_actual_cost_per_hour"
        ]
    }

    

