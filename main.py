import streamlit as st
from streamlit_option_menu import option_menu
# from page import home, query, rule
from page import home, query
from api import get_v1_localization_key
from api import get_v1_config, get_v2_config
from common_handling import set_lockey

st.session_state.localization_key = get_v1_localization_key.execute()['data']
st.session_state.config = get_v2_config.execute()['data']

lockey = set_lockey.execute

st.set_page_config(page_title=lockey("title_page"), layout="wide")

apps = [
    {"func": home.app, "title": lockey("title_home"), "icon": "house"},
    {"func": query.app, "title": lockey("title_query"), "icon": "database"}
    # {"func": rule.app, "title": lockey("title_rule"), "icon": "book"}
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
