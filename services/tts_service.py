import os, sys, requests
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
TTS_ENDPOINT = "https://api.openai.com/v1/audio/speech"
TTS_TIMEOUT = 120


def _api_key() -> str:
    k = os.getenv("OPENAI_API_KEY")
    if not k:
        raise RuntimeError("Set OPENAI_API_KEY in your .env file")
    return k


def synthesize_speech(
    text: str, model: str = TTS_MODEL, voice: str = "alloy", format: str = "mp3"
) -> bytes:
    """Send text to OpenAI TTS and return audio bytes."""
    if not text or not text.strip():
        raise ValueError("Text is empty")

    data = {"model": model, "voice": voice, "input": text, "format": format}

    r = requests.post(
        TTS_ENDPOINT,
        headers={"Authorization": f"Bearer {_api_key()}"},
        json=data,
        timeout=TTS_TIMEOUT,
    )

    if r.status_code != 200:
        raise RuntimeError(f"TTS {r.status_code}: {r.text[:500]}")

    return r.content  # audio bytes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python services/tts_service.py 'Your text here'", file=sys.stderr)
        sys.exit(2)
    try:
        audio_bytes = synthesize_speech(sys.argv[1])
        out_path = "output.mp3"
        with open(out_path, "wb") as f:
            f.write(audio_bytes)
        print(f"✅ Saved TTS to {out_path}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
