import json

def clean_response(response: str) -> dict:
    clean_response = response.replace('```json\n', '').replace('\n```', '')
    return json.loads(clean_response)