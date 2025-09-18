import os, sys, requests
from typing import List, Dict, Optional

try:  # load .env automatically
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# -------- Configuration --------
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
ENDPOINT = "https://api.openai.com/v1/chat/completions"
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
# --------------------------------


def _api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY in your .env file")
    return key


def _post(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL,
          temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
    """Low-level POST to OpenAI API."""
    payload: Dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    r = requests.post(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=TIMEOUT,
    )

    if r.status_code != 200:
        raise RuntimeError(f"OpenAI {r.status_code}: {r.text[:300]}")

    data = r.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected response: {data}") from e


def chat_once(prompt: str, model: str = DEFAULT_MODEL,
              temperature: float = 0.7) -> str:
    """Simple one-shot chat without history."""
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("Prompt is empty")
    return _post([{"role": "user", "content": prompt}],
                 model=model, temperature=temperature)


def chat(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL,
         temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
    """
    Chat with memory — pass full message history:
    messages = [
        {"role": "system", "content": "You are an interviewer..."},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello"}
    ]
    """
    if not messages:
        raise ValueError("Messages list is empty")
    return _post(messages, model=model,
                 temperature=temperature, max_tokens=max_tokens)


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
