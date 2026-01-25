import requests
import json

try:
    print("Sending request to GitHub API...")
    url = "https://api.github.com/repos/commaai/opendbc/contents/"
    # Add a User-Agent, sometimes GitHub blocks scripts without one
    headers = {'User-Agent': 'CANdy-Diag-Pro/1.0'}
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Item count: {len(data)}")
        dbc_files = [f['name'] for f in data if f['name'].endswith('.dbc')]
        print(f"DBC Files found: {len(dbc_files)}")
        if len(dbc_files) > 0:
            print(f"First 5: {dbc_files[:5]}")
        else:
            print("No DBC files found in root.")
            print("All root items:", [f.get('name') for f in data])
            
            # Try /opendbc subfolder
            print("\nChecking /opendbc subfolder...")
            url2 = "https://api.github.com/repos/commaai/opendbc/contents/opendbc"
            resp2 = requests.get(url2, headers=headers)
            if resp2.status_code == 200:
                data2 = resp2.json()
                dbcs2 = [f['name'] for f in data2 if f['name'].endswith('.dbc')]
                print(f"DBCs in /opendbc: {len(dbcs2)}")
                if len(dbcs2) > 0:
                    print(f"First 5: {dbcs2[:5]}")
                else:
                    print("No DBCs in /opendbc.")
                     # Print subdirectories/files in /opendbc
                    print("Items in /opendbc:", [f.get('name') for f in data2])
    else:
        print("Error response:", response.text[:500])
        
except Exception as e:
    print(f"Exception: {e}")
