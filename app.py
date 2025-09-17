import streamlit as st
from tabs import llm_tab, stt_tab, tts_tab

st.set_page_config(page_title="AI Interviewer", layout="wide")

tab_objs = st.tabs(["LLM", "STT", "TTS"])

with tab_objs[0]:
    llm_tab.render()

with tab_objs[1]:
    stt_tab.render()

with tab_objs[2]:
    tts_tab.render()