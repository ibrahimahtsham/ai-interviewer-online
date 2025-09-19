import os
from typing import List, Dict

def get_interview_dir(username: str) -> str:
    """
    Returns the path to the user's interview directory, creating it if necessary.
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    interviews_dir = os.path.join(root, "interviews")
    user_dir = os.path.join(interviews_dir, f"{username}-interview")
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def save_transcript(username: str, history: List[Dict], transcript_filename: str = "transcript.txt") -> str:
    """
    Saves the transcript in the specified format under the user's interview directory.
    history: list of dicts with keys 'role' (either 'assistant' or 'user') and 'content'.
    """
    user_dir = get_interview_dir(username)
    transcript_path = os.path.join(user_dir, transcript_filename)
    lines = []
    for entry in history:
        if entry["role"] == "assistant":
            lines.append(f"AI Interviewer: {entry['content']}")
        elif entry["role"] == "user":
            lines.append(f"{username}: {entry['content']}")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(lines))
    return transcript_path

def save_audio(username: str, entry_idx: int, role: str, audio_bytes: bytes, ext: str = "mp3") -> str:
    """
    Saves an audio file for either the AI or the user in the user's interview directory.
    role: 'assistant' for AI, 'user' for the interviewee.
    ext: file extension, e.g., 'mp3' or 'wav'.
    """
    user_dir = get_interview_dir(username)
    if role == "assistant":
        fname = f"ai-response-{entry_idx}.{ext}"
    else:
        fname = f"{username}-response-{entry_idx}.{ext}"
    audio_path = os.path.join(user_dir, fname)
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)
    return audio_path
