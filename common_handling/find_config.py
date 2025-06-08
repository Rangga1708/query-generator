import streamlit as st

def execute(key):
    try:
        return st.session_state.config[key]
    except:
        return key