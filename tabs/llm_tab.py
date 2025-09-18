import streamlit as st
from services.llm_service import chat_once

def render():
	st.header("🧠 Language Model (LLM)")
	st.write("Enter a prompt and get a single response from the remote model.")

	if "llm_history" not in st.session_state:
		st.session_state.llm_history = []  # list of dicts: {prompt, response}

	with st.form("llm_form"):
		prompt = st.text_area("Prompt", placeholder="e.g. Say ready", height=140)
		submitted = st.form_submit_button("Send")

	if submitted:
		if not prompt.strip():
			st.warning("Please enter a prompt.")
		else:
			try:
				response = chat_once(prompt)
				st.session_state.llm_history.append({"prompt": prompt, "response": response})
			except Exception as e:
				st.error(f"Error: {e}")

	if st.session_state.llm_history:
		st.subheader("History")
		for item in reversed(st.session_state.llm_history):
			st.markdown(f"**You:** {item['prompt']}")
			st.markdown(f"**LLM:** {item['response']}")
			st.markdown("---")