import pandas as pd

def apply_formulae(df, specs):
    """Apply calculation specs to dataframe."""
    out = df.copy()
    print("specsspecs",specs)
    for col, func in specs.items():
        try:
            out[col] = out.apply(func, axis=1)
        except Exception as e:
            print(f"[ERROR] Calculating {col}: {e}")
            out[col] = None
    return out

def _to_numeric(s):
    """Convert Series to numeric, treating blanks/NaN as 0."""
    s = s.replace(r'^\s*$', 0, regex=True)  # blank strings → 0
    s = pd.to_numeric(s, errors="coerce").fillna(0)  # NaN → 0
    return s

def compare_columns(df, compare_pairs, tolerance=0.01):
    """
    Compare local calculated columns to remote columns.
    compare_pairs: list of (local_col, remote_col)
    """
    out = df.copy()
    for local, remote in compare_pairs:
        if local not in out.columns or remote not in out.columns:
            print(f"[WARN] Skipping pair: {local} vs {remote} (missing)")
            continue

        l = _to_numeric(out[local])
        r = _to_numeric(out[remote])

        diff_col  = f"{local}__diff"
        match_col = f"{local}__match"

        out[diff_col]  = l - r
        out[match_col] = out[diff_col].abs() <= tolerance
    return out

def convert_floats_to_int(df, inplace=False):
    """
    Convert all float columns in a DataFrame to int.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame
        round_values (bool): If True, round values before converting to int.
                             If False, truncate decimals.
        inplace (bool): If True, modify the DataFrame directly. 
                        If False, return a new DataFrame.
    """
    target = df if inplace else df.copy()
    float_cols = target.select_dtypes(include=["float"]).columns
    
    for col in float_cols:
        try:
            # make it round about
            # target[col] = target[col].fillna(0).round().astype(int)
            target[col] = target[col].fillna(0).astype(int)
        except Exception as e:
            print(f"[WARN] Could not convert column {col}: {e}")
    
    return target
