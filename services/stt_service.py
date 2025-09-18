import os, sys, requests
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Default to whisper-1 (works with /audio/transcriptions)
STT_MODEL = os.getenv("STT_MODEL", "whisper-1")
STT_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"
STT_TIMEOUT = 120


def _api_key() -> str:
    k = os.getenv("OPENAI_API_KEY")
    if not k:
        raise RuntimeError("Set OPENAI_API_KEY in your .env file")
    return k


def transcribe_audio(
    file_path: str,
    model: str = STT_MODEL,
    language: Optional[str] = None,
    prompt: Optional[str] = None,
) -> str:
    """Send audio file to OpenAI STT (Whisper-1)."""

    if not file_path:
        raise ValueError("file_path is empty")
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    # Only whisper-1 is supported here
    if not model.startswith("whisper"):
        model = "whisper-1"

    data = {"model": model}
    if language:
        data["language"] = language
    if prompt:
        data["prompt"] = prompt

    with open(file_path, "rb") as f:
        files = {
            "file": (os.path.basename(file_path), f, "application/octet-stream")
        }
        r = requests.post(
            STT_ENDPOINT,
            headers={"Authorization": f"Bearer {_api_key()}"},
            data=data,
            files=files,
            timeout=STT_TIMEOUT,
        )

    if r.status_code != 200:
        raise RuntimeError(f"STT {r.status_code}: {r.text[:500]}")

    js = r.json()
    text = js.get("text")
    if not isinstance(text, str):
        raise RuntimeError(f"Unexpected STT response: {js}")
    return text.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python services/stt_service.py path/to/audio", file=sys.stderr)
        sys.exit(2)
    try:
        print(transcribe_audio(sys.argv[1]))
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
