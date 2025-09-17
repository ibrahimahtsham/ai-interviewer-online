import os, sys, requests

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Single model constant (adjust here when you want to switch models)
MODEL = "llama-3.3-70b-versatile"
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def generate_response(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    # Bare bones: assume key is present; if not, this will 401 and raise below
    r = requests.post(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Groq error {r.status_code}: {r.text[:200]}")
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python services/llm_service.py 'your prompt'", file=sys.stderr)
        sys.exit(2)
    print(generate_response(sys.argv[1]))
