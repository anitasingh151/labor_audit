import pandas as pd

def clean_headers(cols):
    s = pd.Series(cols, dtype="object").fillna("")
    s = (s.astype(str).str.strip().str.lower().str.replace(r"\s+", "_", regex=True))
    s = s.mask(s == "", "_")
    seen = {}
    out = []
    for c in s:
        if c not in seen:
            seen[c] = 0
            out.append(c)
        else:
            seen[c] += 1
            out.append(f"{c}_{seen[c]}")
    return out

def ensure_columns(df, *, strict=True, extra_columns=None):
    required = [
        "estimated_quantity",
        "estimated_hours",
        "jtd_quantity",
        "jtd_hours",
        "labor_percent_complete",
    ]
    if extra_columns:
        required.extend(extra_columns)
    missing = [c for c in required if c not in df.columns]
    if strict and missing:
        raise ValueError(
            "Missing required input columns: "
            + ", ".join(missing)
            + "\nTip: check header cleaning or sheet/header row."
        )
    
    missing = [c for c in required if c not in df.columns]
    if strict and missing:
        raise ValueError(
            "Missing required input columns: "
            + ", ".join(missing)
            + "\nTip: check header cleaning or sheet/header row."
        )
    if not strict:
        for col in missing:
            df[col] = 0
            print(f"[WARN] Missing column '{col}' — defaulting to 0.")
    return df

def ensure_compare_columns(df, pairs, *, strict=True):
    missing_remote = [remote for _, remote in pairs if remote not in df.columns]
    if strict and missing_remote:
        raise ValueError(
            "Missing remote comparison columns: "
            + ", ".join(missing_remote)
            + "\nTip: confirm cleaned header names or adjust COMPARE_PAIRS."
        )

def normalize_inclusions(
    df,
    tc_mode=None,
    qty_mode=None,
    tc_subtract_col=None,
    unposted_subtract_col=None,
    *,
    strict=True
):
    out = df.copy()
    headers = set(out.columns)

    def auto_mode(prefix: str):
        inc = f"{prefix}_included" in headers
        exc = f"{prefix}_excluded" in headers
        if inc and not exc:
            return "included"
        if exc and not inc:
            return "excluded"
        return "excluded"

    effective_tc_mode  = tc_mode  or auto_mode("tc_hours")
    effective_qty_mode = qty_mode or auto_mode("unposted_quantity")

    # --- TC hours ---
    if tc_subtract_col is None:
        for cand in ("tc_hours_excluded", "tc_hours", "tc_hours_included"):
            if cand in headers:
                tc_subtract_col = cand
                break
    out["tc_hours_eff"] = out[tc_subtract_col] if (tc_subtract_col and tc_subtract_col in headers) else 0

    if effective_tc_mode == "included":
        if "jtd_hours" in headers and tc_subtract_col in headers:
            out["jtd_hours_eff"] = out["jtd_hours"] - out[tc_subtract_col]
        else:
            if strict:
                raise ValueError(
                    "TC Hours set to INCLUDED but missing one of: 'jtd_hours' or the TC subtract column "
                    f"('{tc_subtract_col or '<<unspecified>>'}')."
                )
            print("[WARN] TC included but subtract column missing; using jtd_hours as-is.")
            out["jtd_hours_eff"] = out["jtd_hours"] if "jtd_hours" in headers else 0
    else:
        out["jtd_hours_eff"] = out["jtd_hours"] if "jtd_hours" in headers else 0

    # --- Unposted quantity ---
    if unposted_subtract_col is None:
        for cand in ("unposted_quantity_excluded", "unposted_quantity", "additional_quantity"):
            if cand in headers:
                unposted_subtract_col = cand
                break

    out["unposted_value_eff"] = (
        out[unposted_subtract_col] if (unposted_subtract_col and unposted_subtract_col in headers) else 0
    )

    if effective_qty_mode == "included":
        if "jtd_quantity" in headers and unposted_subtract_col in headers:
            out["jtd_quantity_eff"] = out["jtd_quantity"] - out["unposted_value_eff"]
        else:
            if strict:
                raise ValueError(
                    "Unposted Quantity set to INCLUDED but missing one of: 'jtd_quantity' or the Unposted subtract column "
                    f"('{unposted_subtract_col or '<<unspecified>>'}')."
                )
            print("[WARN] Unposted included but subtract column missing; using jtd_quantity as-is.")
            out["jtd_quantity_eff"] = out["jtd_quantity"] if "jtd_quantity" in headers else 0
    else:
        out["jtd_quantity_eff"] = out["jtd_quantity"] if "jtd_quantity" in headers else 0

    return out

import pandas as pd


