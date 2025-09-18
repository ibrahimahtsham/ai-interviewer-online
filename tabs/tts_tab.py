import streamlit as st
from services import tts_service


def render():
    st.header("🗣️ Text-to-Speech (TTS)")

    if "tts_history" not in st.session_state:
        st.session_state.tts_history = []

    text = st.text_area("Enter text to synthesize", height=100)

    col1, col2 = st.columns(2)
    voice = col1.selectbox("Voice", ["alloy", "verse", "bright", "calm"])
    format = col2.selectbox("Format", ["mp3", "wav"])

    if st.button("Generate Speech"):
        if not text.strip():
            st.warning("Please enter some text")
        else:
            try:
                audio_bytes = tts_service.synthesize_speech(
                    text, voice=voice, format=format
                )

                # Play result
                st.audio(audio_bytes, format=f"audio/{format}")

                # Save history
                st.session_state.tts_history.append(
                    {"text": text, "voice": voice, "format": format, "audio_bytes": audio_bytes}
                )
                st.success("✅ Speech generated")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

    if st.session_state.tts_history:
        st.subheader("History")
        for idx, item in enumerate(reversed(st.session_state.tts_history)):
            with st.expander(f"{item['voice']} - {item['text'][:30]}...", expanded=False):
                st.audio(item["audio_bytes"], format=f"audio/{item['format']}")
