import requests

def call_api_testing():
    try:
        response = requests.get('http://localhost:5000/api/costs')
        response.raise_for_status()
        print("[INFO] API response received.")
        cost_data = response.json()
        print("[INFO] API Data:", cost_data)
        cost_type = cost_data[0].get('cost_type')
        return cost_type    
    except Exception as e:
        print(f"API error: {e}")
        return None