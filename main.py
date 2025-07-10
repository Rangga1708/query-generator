import streamlit as st
import hashlib
from streamlit_option_menu import option_menu
from page import home, query, rule
from api import get_v1_localization_key
from common_handling import set_lockey

def input_password():
    with st.form(key = "Input Password", clear_on_submit = True):
        password = st.text_input(
            label = lockey("title_input_password"),
            type = "password"
        )

        if st.form_submit_button(label = lockey("title_login")):
            password = eval(st.secrets["ENCODE"])
            if password == st.secrets["PASSWORD"]:
                st.session_state.password = password
                st.rerun()
            else:
                st.toast(lockey("title_wrong_password_error"), icon = ":material/error:")

def show_page():
    apps = [
        {"func": home.app, "title": lockey("title_home"), "icon": "house"},
        {"func": query.app, "title": lockey("title_query"), "icon": "database"},
        {"func": rule.app, "title": lockey("title_rule"), "icon": "book"}
    ]

    titles = [app["title"] for app in apps]
    titles_lower = [title.lower() for title in titles]
    icons = [app["icon"] for app in apps]

    params = st.query_params

    if "page" in params:
        default_index = int(titles_lower.index(params["page"][0].lower()))
    else:
        default_index = 0

    with st.sidebar:
        selected = option_menu(
            lockey("title_main_menu"),
            options=titles,
            icons=icons,
            menu_icon="cast",
            default_index=default_index,
        )

    for app in apps:
        if app["title"] == selected:
            app["func"]()
            break

if __name__ == "__main__":
    st.set_page_config(page_title = "Query Generator", layout = "wide")

    if "localization_key" not in st.session_state:
        st.session_state.localization_key = get_v1_localization_key.execute()['data']
    
    lockey = set_lockey.execute
    
    if "password" not in st.session_state:
        input_password()
    else:
        show_page()