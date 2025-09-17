# AI Interviewer Online

## Purpose
AI Interviewer Online is a hardware‑agnostic Streamlit application for interview‑style interaction with a remote Language Model (LLM) plus future Speech‑to‑Text (STT) and Text‑to‑Speech (TTS) features. It is intentionally designed to run on low‑spec machines by delegating all heavy AI workloads to online/cloud services.

## Philosophy / Design Principles
- Cloud / online only: no local large model downloads or GPU requirements.
- Lightweight local footprint: Streamlit for UI + thin Python service clients.
- Separation of concerns: pure Python service modules (callable standalone) + UI pages that just orchestrate inputs/outputs.
- Pluggable providers: swap LLM/STT/TTS endpoints via environment variables without code rewrites.
- Fast onboarding: one‑command run scripts for Windows & Linux/macOS.

## Current File Structure
```
ai-interviewer-online
├── app.py
├── tabs
│   ├── llm_tab.py
│   ├── stt_tab.py
│   └── tts_tab.py
├── services
│   ├── llm_service.py
│   ├── stt_service.py
│   └── tts_service.py
├── requirements.txt
├── run.sh
├── run.bat
├── .gitignore
└── README.md
```

## Service Layer (Non-UI Python Modules)
All files under `services` are strict Python modules without any Streamlit dependency. They can be imported or executed directly for testing (e.g. `python services/llm_service.py`). Streamlit tabs simply call these modules' functions to:
1. Send user input (text / audio file path / text for synthesis).
2. Receive structured outputs (model response text / transcription result / audio file path or bytes).

Example usage (interactive shell):
```bash
python
>>> from services.llm_service import generate_response  # placeholder
>>> # generate_response("Hello, can you summarize the purpose of this app?")
```

## Quick Start (Automated)
Linux / macOS:
```bash
./run.sh
```
Windows:
```bat
run.bat
```
The scripts will:
1. Check Python availability.
2. Create a `.venv` virtual environment if missing.
3. Upgrade `pip` and install dependencies.
4. Launch the Streamlit app.

## Manual Setup (Alternative)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```