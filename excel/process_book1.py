import requests
import json
import os

url = 'http://127.0.0.1:5000/upload'
input_file = 'Book1.xlsx'
output_file = 'output.json'

if not os.path.exists(input_file):
    print(f"Error: {input_file} not found.")
    exit(1)

try:
    with open(input_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            # Save to separate JSON file
            with open(output_file, 'w') as out:
                json.dump(data, out, indent=2)
            print(f"Successfully converted {input_file} to {output_file}")
            # Print first few items to verify
            print("Preview of data:")
            print(json.dumps(data[:2], indent=2))
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")
