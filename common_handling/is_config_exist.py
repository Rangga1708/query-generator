import streamlit as st
from common_handling import set_lockey

lockey = set_lockey.execute

def execute():
    if "config" not in st.session_state:
        st.error(lockey("common_error_empty_data"))
        return False
    else:
        return True