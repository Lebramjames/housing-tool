# %%
import os
import argparse
import base64
import json

def decode_base64_to_json(encoded_data):
    decoded_bytes = base64.b64decode(encoded_data)
    json_data = decoded_bytes.decode('utf-8')
    return json.loads(json_data)

def encode_json_to_base64(data):
    json_data = json.dumps(data)
    encoded_bytes = base64.b64encode(json_data.encode('utf-8'))
    return encoded_bytes.decode('utf-8')

def encode_json_to_base64_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return encode_json_to_base64(data)

if __name__ == "__main__":
    google_service_key = os.getenv("GOOGLE_SERVICE_JSON_KEY", None)
    if google_service_key:
        decoded_key = decode_base64_to_json(google_service_key)
        print(f"Decoded Google Service JSON Key: {decoded_key}")
    else:
        print("GOOGLE_SERVICE_JSON_KEY environment variable not set.")