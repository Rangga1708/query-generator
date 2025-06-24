import streamlit as st
from common_handling import set_lockey

lockey = set_lockey.execute

def execute():
    if "password" not in st.session_state:
        st.error(lockey("common_error_empty_password"))
        return False
    else:
        return True