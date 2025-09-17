import streamlit as st
from src.services.llm_service import query_llm

st.title("Language Model Interaction")

st.write("Enter your text below to interact with the language model:")

user_input = st.text_area("Input Text", height=150)

if st.button("Submit"):
    if user_input:
        response = query_llm(user_input)
        st.write("Response from Language Model:")
        st.write(response)
    else:
        st.warning("Please enter some text before submitting.")