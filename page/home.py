import streamlit as st
from common_handling import set_lockey
from common_handling import is_password_valid

lockey = set_lockey.execute

def app():
    if not is_password_valid.execute():
        return {}

    st.title(lockey("home_title_welcome"))

    st.markdown(
        f"""
        This app is used for product owner and QA to generate query by themselves.
        Here are the steps to generate the query:
        1. Go to **Create Rule** menu
        2. Go to **Import Feature** tab
        3. Import the JSON file (You can download it from [here]({st.secrets["JSON_URL"]})
        4. Click **Save**
        5. Go to **Create Query** menu
        6. Find the feature you want and follow the notes
        \n\n
        When executing query, always follow these rules:
        1. Use query SELECT first to check existing data
        2. Execute the query INSERT/UPDATE/MERGE
        3. Use query SELECT again to recheck after executing the query
        4. If there is any problem or concern, please ask AD
        """
    )