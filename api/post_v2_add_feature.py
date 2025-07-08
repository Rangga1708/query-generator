import pandas as pd
import streamlit as st
from streamlit_javascript import st_javascript
from common_handling import set_lockey
from common_handling import response
from common_handling import find_config
from common_handling import find_value_in_dataframe

lockey = set_lockey.execute
config = find_config.execute

def execute(request):
    if not is_request_valid(request):
        return response.execute(
            status = "30001",
            message = lockey("rule_label_invalid_input"),
            data = {}
        ) 
    
    if is_feature_exist(request):
        return response.execute(
            status = "30002",
            message = lockey("rule_label_feature_already_exist"),
            data = {}
        )
    
    st.session_state.config["features"].append(request)

    st_javascript(f"""await localStorage.setItem("features", JSON.stringify({config("features")}));""")

    return response.execute(
            status = "200",
            message = lockey("rule_label_add_new_feature_success"),
            data = {}
        )
    
def is_request_valid(request):
    return request["name"] != ''

def is_feature_exist(request):
    features = pd.DataFrame(config("features"))

    if len(features) == 0:
        return False
    else:
        return len(find_value_in_dataframe.execute(data = features, search_value = request["name"], reference_column = "name")) != 0