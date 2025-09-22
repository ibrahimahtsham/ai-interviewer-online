import streamlit as st
import tempfile
from services import llm_service, tts_service, stt_service
from streamlit_mic_recorder import mic_recorder
from utilities import interview_utility


def render():
    # --- Track last played assistant audio index to prevent double playback ---
    if "last_played_ai_idx" not in st.session_state:
        st.session_state.last_played_ai_idx = -1
    st.set_page_config(page_title="AI Interviewer", layout="wide")
    st.title("💼 AI Interviewer")

    # --- Initialize session state ---
    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []
    if "interview_role" not in st.session_state:
        st.session_state.interview_role = None
    if "candidate_name" not in st.session_state:
        st.session_state.candidate_name = None
    if "draft_reply" not in st.session_state:
        st.session_state.draft_reply = ""
    if "last_audio" not in st.session_state:
        st.session_state.last_audio = None  # stores raw bytes from mic

    # --- Restart option ---
    if st.session_state.interview_role and st.session_state.candidate_name:
        if st.button("🔄 Restart Interview"):
            st.session_state.clear()
            st.rerun()

    # --- Name and Role selection ---
    if not st.session_state.candidate_name or not st.session_state.interview_role:
        st.subheader("👤 Enter Your Details to Begin")
        name_input = st.text_input("Your Name")
        role_input = st.text_input("Job Role (e.g., Software Engineer, Data Scientist)")
        if st.button("Start Interview"):
            if not name_input.strip() or not role_input.strip():
                st.warning("Please enter both your name and the job role.")
            else:
                st.session_state.candidate_name = name_input.strip()
                st.session_state.interview_role = role_input.strip()

                # Add system instruction (still needed for LLM context, but not used for opener)
                st.session_state.interview_history.append({
                    "role": "system",
                    "content": (
                        f"You are a professional interviewer for the role of {role_input}. "
                        f"The candidate's name is {name_input}. "
                        "Ask only one single, relevant interview question for this role. "
                        "Do not answer on behalf of the candidate."
                    )
                })

                # Use hardcoded opener with variables
                opener = f"Welcome {name_input}, thank you for interviewing for the {role_input} position. Let's begin."
                try:
                    audio_bytes = tts_service.synthesize_speech(opener)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
                    return

                st.session_state.interview_history.append(
                    {"role": "assistant", "content": opener, "audio": audio_bytes}
                )
                # Save initial transcript and AI audio
                interview_utility.save_transcript(st.session_state.candidate_name, st.session_state.interview_history)
                interview_utility.save_audio(
                    st.session_state.candidate_name,
                    1,
                    "assistant",
                    audio_bytes,
                    ext="mp3"
                )
                st.rerun()
        return

    # --- Conversation UI ---
    st.subheader(f"Interview for: {st.session_state.interview_role} (Candidate: {st.session_state.candidate_name})")

    # --- Display chat history with auto-play for assistant audio ---
    last_idx = len(st.session_state.interview_history) - 1
    # Render all but the last message
    for idx, entry in enumerate(st.session_state.interview_history[:-1]):
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.write(entry["content"])
                if entry.get("audio"):
                    st.audio(entry["audio"], format="audio/wav")
        elif entry["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(entry["content"])
                if entry.get("audio"):
                    st.audio(entry["audio"], format="audio/mp3")

    # Render the last message (if any), with autoplay only if not already played
    if last_idx >= 0:
        entry = st.session_state.interview_history[last_idx]
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.write(entry["content"])
                if entry.get("audio"):
                    st.audio(entry["audio"], format="audio/wav")
        elif entry["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(entry["content"])
                if entry.get("audio"):
                    # Only autoplay if this is a new assistant message
                    if st.session_state.last_played_ai_idx != last_idx:
                        import base64
                        audio_b64 = base64.b64encode(entry["audio"]).decode("utf-8")
                        audio_html = f'''
                        <audio id="ai-audio" src="data:audio/mp3;base64,{audio_b64}" autoplay controls style="width: 100%; margin-top: 0.5em;"></audio>
                        <script>
                        var audio = document.getElementById('ai-audio');
                        if (audio) {{
                            audio.autoplay = true;
                            audio.play().catch(()=>{{}});
                        }}
                        </script>
                        '''
                        st.markdown(audio_html, unsafe_allow_html=True)
                        st.session_state.last_played_ai_idx = last_idx
                    else:
                        st.audio(entry["audio"], format="audio/mp3")

    st.divider()

    # --- End Interview Button ---
    if "interview_ended" not in st.session_state:
        st.session_state.interview_ended = False

    if not st.session_state.interview_ended:
        if st.button("End Interview Here"):
            closer = f"Thank you, {st.session_state.candidate_name}, for your time. This concludes your interview for the {st.session_state.interview_role} position."
            try:
                closer_audio = tts_service.synthesize_speech(closer)
            except Exception as e:
                st.error(f"⚠️ TTS Error: {e}")
                return
            st.session_state.interview_history.append({"role": "assistant", "content": closer, "audio": closer_audio})
            ai_entries = [e for e in st.session_state.interview_history if e["role"] == "assistant"]
            ai_idx = len(ai_entries)
            interview_utility.save_audio(st.session_state.candidate_name, ai_idx, "assistant", closer_audio, ext="mp3")
            st.session_state.interview_ended = True
            interview_utility.save_transcript(st.session_state.candidate_name, st.session_state.interview_history)
            st.rerun()

    # --- Mic Recorder with auto-send after recording ---
    if not st.session_state.interview_ended:
        st.subheader("🎤 Record Your Reply")
        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            key=f"mic_{len(st.session_state.interview_history)}",  # unique key per turn
        )

        # If audio is recorded, auto-transcribe and auto-send
        if audio and audio.get("bytes"):
            st.session_state.last_audio = audio["bytes"]
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(st.session_state.last_audio)
                    path = tmp.name
                text = stt_service.transcribe_audio(path)
                st.session_state.draft_reply = text
                # st.success("✅ Transcribed and loaded into input box")
            except Exception as e:
                st.error(f"⚠️ STT Error: {e}")
                return

            user_msg = st.session_state.draft_reply
            if not user_msg.strip() and not st.session_state.last_audio:
                st.warning("Please type or record a reply first.")
                return

            # Save user entry (with text + audio)
            st.session_state.interview_history.append({
                "role": "user",
                "content": user_msg.strip(),
                "audio": st.session_state.last_audio,
            })
            st.session_state.draft_reply = ""
            st.session_state.last_audio = None

            # Build convo
            messages = [
                {"role": h["role"], "content": h["content"]}
                for h in st.session_state.interview_history
            ]

            try:
                llm_reply = llm_service.chat(messages)
                audio_bytes = tts_service.synthesize_speech(llm_reply)
            except Exception as e:
                st.error(f"⚠️ LLM Error: {e}")
                return

            st.session_state.interview_history.append(
                {"role": "assistant", "content": llm_reply, "audio": audio_bytes}
            )

            # Save transcript and audio files after each exchange
            username = st.session_state.candidate_name
            interview_utility.save_transcript(username, st.session_state.interview_history)
            user_entries = [e for e in st.session_state.interview_history if e["role"] == "user"]
            ai_entries = [e for e in st.session_state.interview_history if e["role"] == "assistant"]
            user_idx = len(user_entries)
            ai_idx = len(ai_entries)
            last_user = user_entries[-1] if user_entries else None
            last_ai = ai_entries[-1] if ai_entries else None
            if last_user and last_user.get("audio"):
                interview_utility.save_audio(
                    username,
                    user_idx,
                    "user",
                    last_user["audio"],
                    ext="wav"
                )
            if last_ai and last_ai.get("audio"):
                interview_utility.save_audio(
                    username,
                    ai_idx,
                    "assistant",
                    last_ai["audio"],
                    ext="mp3"
                )

            st.rerun()
        else:
            # If no audio, show text input as fallback
            user_msg = st.text_input(
                "Type or edit your reply:",
                value=st.session_state.draft_reply,
                key="chat_input",
            )
            if st.button("Send Reply"):
                if not user_msg.strip() and not st.session_state.last_audio:
                    st.warning("Please type or record a reply first.")
                    return
                st.session_state.interview_history.append({
                    "role": "user",
                    "content": user_msg.strip(),
                    "audio": st.session_state.last_audio,
                })
                st.session_state.draft_reply = ""
                st.session_state.last_audio = None
                messages = [
                    {"role": h["role"], "content": h["content"]}
                    for h in st.session_state.interview_history
                ]
                try:
                    llm_reply = llm_service.chat(messages)
                    audio_bytes = tts_service.synthesize_speech(llm_reply)
                except Exception as e:
                    st.error(f"⚠️ LLM Error: {e}")
                    return
                st.session_state.interview_history.append(
                    {"role": "assistant", "content": llm_reply, "audio": audio_bytes}
                )
                username = st.session_state.candidate_name
                interview_utility.save_transcript(username, st.session_state.interview_history)
                user_entries = [e for e in st.session_state.interview_history if e["role"] == "user"]
                ai_entries = [e for e in st.session_state.interview_history if e["role"] == "assistant"]
                user_idx = len(user_entries)
                ai_idx = len(ai_entries)
                last_user = user_entries[-1] if user_entries else None
                last_ai = ai_entries[-1] if ai_entries else None
                if last_user and last_user.get("audio"):
                    interview_utility.save_audio(
                        username,
                        user_idx,
                        "user",
                        last_user["audio"],
                        ext="wav"
                    )
                if last_ai and last_ai.get("audio"):
                    interview_utility.save_audio(
                        username,
                        ai_idx,
                        "assistant",
                        last_ai["audio"],
                        ext="mp3"
                    )
                st.rerun()
