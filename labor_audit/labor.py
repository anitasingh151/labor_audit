from config import THRESHOLD
import pandas as pd

# fields are common in labor and cost
def percent_of_quantity(estimated_quantity, jtd_quantity, unposted_quantity_excluded):
    """(JTD Qty (excluded) + Unposted) / Estimated Qty * 100"""
    if not estimated_quantity or estimated_quantity == 0:
        return 0
    return (jtd_quantity + unposted_quantity_excluded) / estimated_quantity * 100

# Common fields in labor and cost : estimated_hours, labor_percent_complete
def earned_hours(estimated_hours, labor_percent_complete):
    """Estimated Hours * Labor % Complete / 100"""
    if estimated_hours is None or labor_percent_complete is None:
        return 0
    return estimated_hours * labor_percent_complete / 100

# LABOR Only, uses local_earned_hours.
def actual_over_earned(jtd_hours, tc_hours_excluded, local_earned_hours):
    """JTD Hours (excluded) / Earned Hours"""
    if not local_earned_hours or local_earned_hours == 0:
        return 0
    return (jtd_hours + tc_hours_excluded) / local_earned_hours

# Common Fields: labor_percent_complete, estimated_hours, jtd_hours
def projected_hours_at_complete(labor_percent_complete, estimated_hours, jtd_hours, tc_hours_excluded, threshold=THRESHOLD):
    """Calculate Projected Hours At Complete for labor types.
    Uses total JTD hours = jtd_hours + tc_hours_excluded."""
    total_jtd_hours = jtd_hours + tc_hours_excluded
    if labor_percent_complete < threshold:
        return max(estimated_hours, total_jtd_hours)
    if labor_percent_complete == 0:
        return 0
    return total_jtd_hours / (labor_percent_complete / 100)

# Common Fields: local_earned_hours, estimated_hours, jtd_hours
def earned_hours_over_under(jtd_hours, tc_hours_excluded, earned_hours):
    """JTD Hours (excluded) - Earned Hours"""
    if jtd_hours is None or tc_hours_excluded is None or earned_hours is None:
        return 0
    return (jtd_hours + tc_hours_excluded) - earned_hours


# LABOR Only: local_projected_hours_at_complete, estimated_hours
def projected_hours_over_under(local_projected_hours_at_complete, estimated_hours):
    """Projected At Complete - Estimated Hours"""
    if local_projected_hours_at_complete is None or estimated_hours is None:
        return 0
    return local_projected_hours_at_complete - estimated_hours

# Common Fields : estimated_hours, jtd_hours, tc_hours_excluded
def percent_of_estimate(estimated_hours, jtd_hours, tc_hours_excluded):
    """(JTD Hours (excluded) + TC Hours) / Estimated Hours * 100"""
    if not estimated_hours or estimated_hours == 0:
        return 0
    return (jtd_hours + tc_hours_excluded) / estimated_hours * 100

# Common Fields
def jtd_production(estimated_quantity, estimated_hours, jtd_quantity, unposted_quantity_excluded, jtd_hours, tc_hours_excluded):
    """
    If Est Qty > Est Hours:
        (JTD Qty (excluded) + Unposted) / (JTD Hours (excluded) + TC Hours)
    Else:
        (JTD Hours (excluded) + TC Hours) / (JTD Qty (excluded) + Unposted)
    """
    if estimated_quantity > estimated_hours:
        denom = jtd_hours + tc_hours_excluded
        if denom == 0:
            return 0
        return (jtd_quantity + unposted_quantity_excluded) / denom
    else:
        numer = jtd_hours + tc_hours_excluded
        denom = jtd_quantity + unposted_quantity_excluded
        if denom == 0:
            return 0
        return numer / denom

# Common Fields
def estimated_hours_remaining(estimated_hours, tc_hours_excluded, jtd_hours):
    """Estimated Hours - TC Hours - JTD Hours (excluded)"""
    if estimated_hours is None or tc_hours_excluded is None or jtd_hours is None:
        return 0
    return estimated_hours - tc_hours_excluded - jtd_hours

# Common Fields
def estimated_production(estimated_quantity, estimated_hours):
    """
    If Est Qty > Est Hours: Est Qty / Est Hours (guard 0)
    Else: Est Hours / Est Qty (guard 0)
    """
    if estimated_quantity > estimated_hours:
        if not estimated_hours or estimated_hours == 0:
            return 0
        return estimated_quantity / estimated_hours
    else:
        if not estimated_quantity or estimated_quantity == 0:
            return 0
        return estimated_hours / estimated_quantity

# Common Fields
def projected_hours_to_complete(local_projected_hours_at_complete,jtd_hours,tc_hours_excluded):
    """
    create logic for Projected_Hours_To_Complete = Projected_Hours_At_Complete - JTD_Total_Hours, and
    jtd_total_hours = jtd_hours_eff + tc_hours_eff
    """
    # jtd_total_hours = jtd_hours_eff + tc_hours_eff
    if local_projected_hours_at_complete is None or jtd_hours is None:
        return 0
    return local_projected_hours_at_complete - (jtd_hours + tc_hours_excluded)

# COST Only: estimated_hours, current_estimated_cost
def estimated_cost_per_hour(estimated_hours, current_estimated_cost):
    if not estimated_hours or estimated_hours == 0:
        return 0
    return current_estimated_cost / estimated_hours

# COST Only
def variance_cost_per_hour(projected_cost_jsf, current_estimated_cost):
    return projected_cost_jsf - current_estimated_cost

# COST Only
def local_percent_of_cost(jtd_actual_cost, current_estimated_cost):
    if pd.isna(current_estimated_cost) or current_estimated_cost == 0:
        return 0
    if pd.isna(jtd_actual_cost):
        return 0
    return (jtd_actual_cost / current_estimated_cost) * 100

# COST Only, JSON Mapping is happening
def actual_cost_per_hour(jtd_hours, jtd_actual_dollars, estimated_hours):
    """
    Calculate actual cost per hour:
    1. If jtd_hours == 0 OR jtd_actual_dollars == 0:
        - If estimated_hours != 0: use (jtd_actual_dollars / estimated_hours)
    2. Else (both non-zero):
        - If jtd_hours != 0: use (jtd_actual_dollars / jtd_hours)
    """
    if (jtd_hours == 0 or jtd_actual_dollars == 0):
        if estimated_hours != 0:
            return jtd_actual_dollars / estimated_hours
        else:
            return 0
    else:
        if jtd_hours != 0:
            return jtd_actual_dollars / jtd_hours
        else:
            return 0

# ___________New Changes [29 May 2026]_________________
def projected_to_complete(
    projected_hours_at_complete,
    jtd_hours,
    tc_hours_excluded
):
    """
    Projected_Hours_To_Complete =
        Projected_Hours_At_Complete - (JTD_Hours + TC_Hours_Excluded)
    """
    jtd_total_hours = jtd_hours + tc_hours_excluded
    return projected_hours_at_complete - jtd_total_hours

def jtd_production_new(
    estimated_quantity,
    estimated_hours,
    jtd_quantity_eff,
    unposted_quantity_eff,
    jtd_hours_eff,
    tc_hours_eff
):
    """
    Total_JTD_Hours = JTD_Hours + TC_Hours_Excluded
    Total_JTD_Quantity = JTD_Quantity + Unposted_Quantity_Excluded

    If Estimated_Quantity = 0:
        If Total_JTD_Quantity > Total_JTD_Hours:
            JTD_Production = Total_JTD_Quantity / Total_JTD_Hours
        Else:
            JTD_Production = Total_JTD_Hours / Total_JTD_Quantity

    Else If Estimated_Quantity > Estimated_Hours:
        JTD_Production = Total_JTD_Quantity / Total_JTD_Hours

    Else:
        JTD_Production = Total_JTD_Hours / Total_JTD_Quantity
    """

    total_jtd_hours = jtd_hours_eff + tc_hours_eff
    total_jtd_quantity = jtd_quantity_eff + unposted_quantity_eff

    # Estimated Quantity = 0
    if estimated_quantity == 0:

        if total_jtd_quantity > total_jtd_hours:
            if total_jtd_hours == 0:
                return 0
            return total_jtd_quantity / total_jtd_hours

        else:
            if total_jtd_quantity == 0:
                return 0
            return total_jtd_hours / total_jtd_quantity

    # Estimated Quantity > Estimated Hours
    elif estimated_quantity > estimated_hours:

        if total_jtd_hours == 0:
            return 0

        return total_jtd_quantity / total_jtd_hours

    # Estimated Quantity <= Estimated Hours
    else:

        if total_jtd_quantity == 0:
            return 0

        return total_jtd_hours / total_jtd_quantity

def labor_specs():
    return {
        "local_percent_of_quantity": lambda r: percent_of_quantity(
            r["estimated_quantity"], r["jtd_quantity"], r["unposted_quantity_excluded"]
        ),

        "local_earned_hours": lambda r: earned_hours(
            r["estimated_hours"], r["labor_percent_complete"]
        ),

        "local_actual_over_earned": lambda r: actual_over_earned(
            r["jtd_hours"], r["tc_hours_excluded"], r["local_earned_hours"]
        ),

        "local_projected_hours_at_complete": lambda r: projected_hours_at_complete(
            r["labor_percent_complete"], r["estimated_hours"], r["jtd_hours"], r["tc_hours_excluded"]
        ),

        "local_earned_hours_over_under": lambda r: earned_hours_over_under(
            r["jtd_hours"], r["tc_hours_excluded"], r["earned_hours"]
        ),

        "local_projected_hours_over_under": lambda r: projected_hours_over_under(
            r["local_projected_hours_at_complete"], r["estimated_hours"]
        ),

        "local_percent_of_estimate": lambda r: percent_of_estimate(
            r["estimated_hours"], r["jtd_hours"], r["tc_hours_excluded"]
        ),

        "local_jtd_production": lambda r: jtd_production(
            r["estimated_quantity"], r["estimated_hours"],
            r["jtd_quantity"], r["unposted_quantity_excluded"],
            r["jtd_hours"], r["tc_hours_excluded"]
        ),

        "local_estimated_hours_remaining": lambda r: estimated_hours_remaining(
            r["estimated_hours"], r["tc_hours_excluded"], r["jtd_hours"]
        ),

        "local_estimated_production": lambda r: estimated_production(
            r["estimated_hours"], r["estimated_quantity"]
        ),


        "local_projected_hours_to_complete": lambda r: projected_hours_to_complete(
            r["local_projected_hours_at_complete"], r["jtd_hours"], r["tc_hours_excluded"]
        ),
        

        "local_estimated_cost_per_hour": lambda row: estimated_cost_per_hour(
            row["estimated_hours"], row["current_estimated_cost"]),

        "variance_cost_per_hour": lambda row: variance_cost_per_hour(
            row["projected_cost_jsf"], row["current_estimated_cost"]),

        "local_percent_of_cost": lambda row: local_percent_of_cost(
            row["jtd_actual_cost"], row["current_estimated_cost"]),

        "local_actual_cost_per_hour": lambda row: actual_cost_per_hour(
            row["jtd_hours"], 
            row["jtd_actual_dollars"],
            row["estimated_hours"]),


# New Fields Added [29th May 2026]
        "local_projected_h_to_complete": lambda r: projected_to_complete(
            r["projected_at_complete"],
            r["jtd_hours"],
            r["tc_hours_excluded"]
        ),

        "local_jtd_production_new": lambda r: jtd_production(
            r["estimated_quantity"],
            r["estimated_hours"],
            r["jtd_quantity"],
            r["unposted_quantity_excluded"],
            r["jtd_hours"],
            r["tc_hours_excluded"]
        ),
        
    }

