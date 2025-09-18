import streamlit as st
import tempfile, time
from services import stt_service
from streamlit_mic_recorder import mic_recorder


def render():
    st.header("🎙️ Speech-to-Text (STT)")

    if "stt_history" not in st.session_state:
        st.session_state.stt_history = []

    # --- Microphone Recorder ---
    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        use_container_width=True,
    )

    if audio and audio.get("bytes"):
        # Playback (WAV)
        st.audio(audio["bytes"], format="audio/wav")

        if st.button("Transcribe Recording"):
            try:
                # Save as WAV (correct format)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio["bytes"])
                    path = tmp.name

                # Transcribe
                text = stt_service.transcribe_audio(path)

                # Store in history
                name = f"mic_{int(time.time())}.wav"
                st.session_state.stt_history.append(
                    {"name": name, "text": text, "audio_bytes": audio["bytes"]}
                )

                st.success("✅ Transcription complete")
                st.markdown(f"**Result:** {text}")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

    # --- History ---
    if st.session_state.stt_history:
        st.subheader("History")
        for item in reversed(st.session_state.stt_history):
            with st.expander(item["name"], expanded=False):
                st.write(item["text"])
                if item.get("audio_bytes"):
                    st.audio(item["audio_bytes"], format="audio/wav")
