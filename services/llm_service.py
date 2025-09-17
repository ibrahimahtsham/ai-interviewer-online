import os, sys, requests
from typing import List, Dict, Any

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

MODEL = "llama-3.3-70b-versatile"  # Adjust here to change base model
ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

def get_api_key() -> str:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("Missing GROQ_API_KEY environment variable.")
    return key

def call_groq_chat(model: str, messages: List[Dict[str, str]], timeout: int = 60) -> str:
    r = requests.post(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
        },
        timeout=timeout,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Groq error {r.status_code}: {r.text[:200]}")
    data: Dict[str, Any] = r.json()
    return data["choices"][0]["message"]["content"].strip()

def chat_once(prompt: str, model: str = MODEL) -> str:
    p = prompt.strip()
    if not p:
        raise ValueError("Prompt is empty.")
    return call_groq_chat(model, [{"role": "user", "content": p}])

# Backward compatible original function name
def generate_response(prompt: str) -> str:  # pragma: no cover - thin wrapper
    return chat_once(prompt)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python services/llm_service.py 'your prompt'", file=sys.stderr)
        sys.exit(2)
    prompt_arg = " ".join(sys.argv[1:])
    try:
        print(chat_once(prompt_arg))
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
