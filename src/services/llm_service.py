import requests

class LLMService:
    def __init__(self, api_url):
        self.api_url = api_url

    def generate_response(self, prompt):
        payload = {
            "prompt": prompt,
            "max_tokens": 150
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('generated_text', '')
        else:
            return f"Error: {response.status_code} - {response.text}"