import json
import uuid
import pandas as pd
import streamlit as st
from common_handling import set_lockey
from common_handling import response
from common_handling import find_config
from common_handling import find_value_in_dataframe
from common_handling import is_config_exist

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
    
    feature_id = str(uuid.uuid4())
    
    request["feature"]["id"] = feature_id

    if not is_config_exist.execute():
        st.session_state.config = {
            "features": [request["feature"]],
            "tables": []
        }
    else:
        st.session_state.config["features"].append(request["feature"])
    
    for table in request["tables"]:
        table["id"] = str(uuid.uuid4())
        table["feature_id"] = feature_id
        st.session_state.config["tables"].append(table)

    return response.execute(
            status = "200",
            message = lockey("rule_label_add_new_feature_success"),
            data = {}
        )
    
def is_request_valid(request):
    print(request)
    if request["feature"]["name"] == '':
        return False
    
    for table in request["tables"]:    
        try:
            table["columns"] = json.loads(table["columns"])
        except:
            return False

        if ((table["table_name"] == '') or
            (table["query_select"] == '') or
            (table["query_execute"] == '') or
            (table["columns"] == [])):
            return False
        
        for column in table["columns"]:
            if (("name" not in column) or
                ("lov" not in column)):
                return False
            elif column["name"] == "":
                return False
            elif type(column["lov"]) != type([]):
                return False
            
    return True

def is_feature_exist(request):
    if not is_config_exist.execute():
        return False

    features = pd.DataFrame(config("features"))

    if len(features) == 0:
        return False
    else:
        return len(find_value_in_dataframe.execute(data = features, search_value = request["feature"]["name"], reference_column = "name")) != 0