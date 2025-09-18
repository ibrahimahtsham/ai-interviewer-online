import os, sys, requests
try:  # load .env automatically (Option A)
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass
from typing import List, Dict

# -------- Configuration (edit here) --------
MODEL = "gpt-4o-mini" # other models: gpt-4o, gpt-4o-2024, gpt-4o-mini, gpt-3.5-turbo
ENDPOINT = "https://api.openai.com/v1/chat/completions"
TIMEOUT = 60 # seconds
# -------------------------------------------

def _api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in your .env file")
    return key

def _post(messages: List[Dict[str, str]], model: str) -> str:
    r = requests.post(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
        json={"model": model, "messages": messages},
        timeout=TIMEOUT,
    )
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI {r.status_code}: {r.text[:200]}")
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

def chat_once(prompt: str, model: str = MODEL) -> str:
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Prompt is empty")
    return _post([{"role": "user", "content": prompt}], model)

def generate_response(prompt: str) -> str:  # backward compatibility
    return chat_once(prompt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python services/llm_service.py 'your prompt'", file=sys.stderr)
        sys.exit(2)
    try:
        print(chat_once(" ".join(sys.argv[1:])))
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
