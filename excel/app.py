from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        try:
            # Read the Excel file
            # engine='openpyxl' is required for xlsx files
            df = pd.read_excel(file, engine='openpyxl')
            
            # Replace NaN values with empty string to match user's requested format
            df = df.fillna('')
            
            # Convert to list of dictionaries (JSON format)
            data = df.to_dict(orient='records')
            
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
