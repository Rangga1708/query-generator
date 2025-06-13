import streamlit as st
from supabase import create_client

def execute():
  url = st.secrets["DATABASE_URL"]
  key = st.secrets["API_KEY"]
  return create_client(url, key)