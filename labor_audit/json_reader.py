import json

def read_labor_json(filepath):
    """
    Extracts company_name, company_Cred_company_id, company_cred_company_code, erpLaborCode_name
    from the labor JSON file.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    result = []
    for item in data.get("data", []):
        company_name = item.get("name")
        company_cred = item.get("companyCredential", {})
        
        # company_Cred_company_id
        company_Cred_company_id = company_cred.get("company_id", "NA")
        
        # company_cred_company_code
        code = company_cred.get("company_code")
        if code is None:
            company_cred_company_code = "NA"
        elif "," in str(code):
            # Convert comma-separated string to tuple of ints
            company_cred_company_code = tuple(int(x) for x in code.split(","))
        else:
            company_cred_company_code = code
        
        # erpLaborCode_name (pick first if list exists)
        erp_labour_codes = item.get("erpLabourCode", [])
        erpLaborCode_name = erp_labour_codes[0]["name"] if erp_labour_codes else "NA"
        
        result.append({
            "company_name": company_name,
            "company_Cred_company_id": company_Cred_company_id,
            "company_cred_company_code": company_cred_company_code,
            "erpLaborCode_name": erpLaborCode_name
        })
    
    # print(f"[INFO] Loaded {len(result)} labor entries from {filepath}\n{result[:3]} ...")
    
    with open("genreated_schema.json", "w") as outfile:
        json.dump({"data": result}, outfile, indent=4)
    return {"data": result}

# Example usage:
read_labor_json("Copyresponse.json")
