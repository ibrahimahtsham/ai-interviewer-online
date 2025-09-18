import streamlit as st
from services import llm_service, tts_service


def render():
    st.header("💬 Interview Chat")

    if "interview_history" not in st.session_state:
        st.session_state.interview_history = []

    if "interview_role" not in st.session_state:
        st.session_state.interview_role = None

    # Clean history (only valid entries)
    st.session_state.interview_history = [
        h for h in st.session_state.interview_history if "role" in h and "content" in h
    ]

    # --- Restart option ---
    if st.session_state.interview_role:
        if st.button("🔄 Restart Interview"):
            st.session_state.interview_history = []
            st.session_state.interview_role = None
            st.rerun()

    # --- Ask for interview role first ---
    if not st.session_state.interview_role:
        st.subheader("🎯 Choose a role to interview for")
        role_input = st.text_input("Enter the job role (e.g., Software Engineer, Data Scientist):")
        if st.button("Start Interview") and role_input.strip():
            st.session_state.interview_role = role_input.strip()

            # Strong system prompt
            st.session_state.interview_history.append({
                "role": "system",
                "content": (
                    f"You are a professional interviewer for the role of {role_input}. "
                    "Your job is to ONLY ask interview questions. "
                    "Do not answer on behalf of the candidate. "
                    "Wait for the candidate (the user) to answer before continuing."
                )
            })

            # First interviewer question
            try:
                llm_reply = llm_service.chat(st.session_state.interview_history)
            except Exception as e:
                st.error(f"⚠️ LLM Error: {e}")
                return

            try:
                audio_bytes = tts_service.synthesize_speech(llm_reply)
            except Exception as e:
                audio_bytes = None
                st.warning(f"TTS failed: {e}")

            st.session_state.interview_history.append(
                {"role": "assistant", "content": llm_reply, "audio": audio_bytes}
            )

            st.rerun()
        return  # stop here until role is chosen

    # --- Chat UI Styles ---
    st.markdown(
        """
        <style>
        .chat-bubble {
            padding: 10px 15px;
            margin: 5px;
            border-radius: 12px;
            max-width: 70%;
            word-wrap: break-word;
            display: inline-block;
        }
        .user-bubble {
            background-color: #2563eb;
            color: white;
            text-align: right;
            float: right;
            clear: both;
        }
        .llm-bubble {
            background-color: #e5e7eb;
            color: black;
            text-align: left;
            float: left;
            clear: both;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Display conversation ---
    for entry in st.session_state.interview_history:
        if entry["role"] == "user":
            st.markdown(f"<div class='chat-bubble user-bubble'>{entry['content']}</div>", unsafe_allow_html=True)
        elif entry["role"] == "assistant":
            st.markdown(f"<div class='chat-bubble llm-bubble'>{entry['content']}</div>", unsafe_allow_html=True)
            if entry.get("audio"):
                st.audio(entry["audio"], format="audio/mp3")

    st.markdown("<div style='clear: both'></div>", unsafe_allow_html=True)

    # --- Input box ---
    with st.form("chat_input", clear_on_submit=True):
        user_msg = st.text_input("Your answer:")
        submitted = st.form_submit_button("Send")

    if submitted and user_msg.strip():
        # Add your answer as user
        st.session_state.interview_history.append({"role": "user", "content": user_msg})

        # Build conversation (exclude audio, keep only role/content)
        messages = []
        for h in st.session_state.interview_history:
            if "role" in h and "content" in h and isinstance(h["content"], str):
                messages.append({"role": h["role"], "content": h["content"]})

        # Get interviewer’s next question
        try:
            llm_reply = llm_service.chat(messages)
        except Exception as e:
            st.error(f"⚠️ LLM Error: {e}")
            return

        try:
            audio_bytes = tts_service.synthesize_speech(llm_reply)
        except Exception as e:
            audio_bytes = None
            st.warning(f"TTS failed: {e}")

        st.session_state.interview_history.append(
            {"role": "assistant", "content": llm_reply, "audio": audio_bytes}
        )

        st.rerun()
