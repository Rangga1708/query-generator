import pandas as pd
import streamlit as st
from common_handling import set_lockey
from common_handling import set_client
from common_handling import response
from common_handling import find_config

lockey = set_lockey.execute
config = find_config.execute

def execute(request):
    if not is_request_valid(request):
        return response.execute(
            status = "30001",
            message = lockey("rule_label_invalid_input"),
            data = {}
        )
    
    features = pd.DataFrame(config("features"))
    tables = pd.DataFrame(config("tables"))

    features.loc[features["id"] == request["feature"]["id"], 
                 ["name", 
                  "notes"]] = [
                      request["feature"]["name"], 
                      request["feature"]["notes"]]

    for table in request["tables"]:
        if len(tables[tables["id"] == table["id"]]) == 0:
            tables.loc[len(tables)] = table
        else:
            tables.loc[tables["id"] == table["id"], 
                ["table_name", 
                "query_select", 
                "query_execute", 
                "columns"]] = [
                    table["table_name"], 
                    table["query_select"], 
                    table["query_execute"], 
                    table["columns"]]

    st.session_state.config["features"] = features.to_dict(orient = "records")
    st.session_state.config["tables"] = tables.to_dict(orient = "records")

    return response.execute(
        status = "200",
        message = lockey("rule_label_update_success"),
        data = {}
    )

def is_request_valid(request):
    if request["feature"]["name"] == '':
        return False
    
    for table in request["tables"]:    
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