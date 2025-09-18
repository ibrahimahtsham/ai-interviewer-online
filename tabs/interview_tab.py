import streamlit as st
import tempfile, time
from services import llm_service, tts_service, stt_service
from streamlit_mic_recorder import mic_recorder


def render():
    st.title("💬 Interview Chat")

    # --- Initialize session state ---
    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []
    if "interview_role" not in st.session_state:
        st.session_state.interview_role = None
    if "draft_reply" not in st.session_state:
        st.session_state.draft_reply = ""

    # --- Restart option ---
    if st.session_state.interview_role:
        if st.button("🔄 Restart Interview"):
            st.session_state.interview_history = []
            st.session_state.interview_role = None
            st.session_state.draft_reply = ""
            st.rerun()

    # --- Role selection ---
    if not st.session_state.interview_role:
        role_input = st.text_input("Enter the job role (e.g., Software Engineer, Data Scientist):")
        if st.button("Start Interview") and role_input.strip():
            st.session_state.interview_role = role_input.strip()

            # Add system message
            st.session_state.interview_history.append({
                "role": "system",
                "content": (
                    f"You are a professional interviewer for the role of {role_input}. "
                    "Only ask interview questions. "
                    "Do not answer on behalf of the candidate. "
                    "Wait for the candidate (the user) to answer."
                )
            })

            # First interviewer question
            try:
                llm_reply = llm_service.chat(st.session_state.interview_history)
            except Exception as e:
                st.error(f"⚠️ LLM Error: {e}")
                return

            # Generate TTS
            try:
                audio_bytes = tts_service.synthesize_speech(llm_reply)
            except Exception:
                audio_bytes = None

            st.session_state.interview_history.append(
                {"role": "assistant", "content": llm_reply, "audio": audio_bytes}
            )
            st.rerun()
        return

    # --- Display conversation ---
    for entry in st.session_state.interview_history:
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.write(entry["content"])
        elif entry["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(entry["content"])
                if entry.get("audio"):
                    st.audio(entry["audio"], format="audio/mp3")

    # --- Mic Recorder ---
    st.subheader("🎤 Record your reply (optional)")
    audio = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        key="mic_recorder",
    )

    if audio and audio.get("bytes"):
        st.audio(audio["bytes"], format="audio/wav")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio["bytes"])
                path = tmp.name
            text = stt_service.transcribe_audio(path)
            st.session_state.draft_reply = text
            st.success("✅ Transcribed from mic")
        except Exception as e:
            st.error(f"⚠️ STT Error: {e}")

    # --- Input box ---
    user_msg = st.text_input("Your answer:", value=st.session_state.draft_reply, key="chat_input")
    if st.button("Send") and user_msg.strip():
        st.session_state.draft_reply = ""
        st.session_state.interview_history.append({"role": "user", "content": user_msg})

        # Build conversation
        messages = [{"role": h["role"], "content": h["content"]}
                    for h in st.session_state.interview_history
                    if "role" in h and "content" in h]

        # LLM reply
        try:
            llm_reply = llm_service.chat(messages)
        except Exception as e:
            st.error(f"⚠️ LLM Error: {e}")
            return

        try:
            audio_bytes = tts_service.synthesize_speech(llm_reply)
        except Exception:
            audio_bytes = None

        st.session_state.interview_history.append(
            {"role": "assistant", "content": llm_reply, "audio": audio_bytes}
        )
        st.rerun()
