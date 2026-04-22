import requests
import platform
import psutil
import socket

def get_specs():
    specs = {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu": platform.processor(),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpus": []
    }
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        for g in gpus:
            specs["gpus"].append(g.name)
        if not gpus:
            specs["gpus"].append("Unknown / Integrated")
    except Exception:
        specs["gpus"].append("Unknown")
        
    return specs

def send_certificate(api_url, max_temps, duration_mins, phases_completed):
    """
    Send the burn-in certificate data to the database API.
    """
    specs = get_specs()
    payload = {
        "status": "SUCCESS",
        "system_specs": specs,
        "max_temperatures": max_temps,
        "test_duration_minutes": duration_mins,
        "phases_completed": phases_completed
    }
    
    try:
        # We will attempt to send to the provided API URL.
        # If no URL is configured, we will just print to console for demonstration.
        if not api_url or api_url == "http://example-api.com/api/certificate":
            print("--- MOCK API REQUEST ---")
            print(f"URL: {api_url}")
            print(f"Payload: {payload}")
            print("------------------------")
            return True
            
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"API Send Error: {e}")
        return False
