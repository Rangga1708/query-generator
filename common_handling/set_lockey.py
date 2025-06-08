import streamlit as st

def execute(key):
    try:
        return st.session_state.localization_key[key]
    except:
        return key