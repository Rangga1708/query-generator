import streamlit as st
import pandas as pd
import uuid
from common_handling import set_lockey, find_config, find_value_in_list_of_dictionary

lockey = set_lockey.execute
config = find_config.execute

def app():
    features_name = [feature["name"] for feature in config("list_of_features")]
    feature = st.selectbox(
        label = lockey("query_label_feature"),
        options = features_name,
        index = None
        )
    
    if feature is None:
        return {}
    elif feature is not None and feature not in features_name:
        st.error(lockey("query_error_feature_not_exist"))
        return {}

    feature_id = find_value_in_list_of_dictionary.execute("name", feature, config("list_of_features"))["id"]

    if feature_id == "vidcall-1":
        execute_vidcall_1()
                
def find_feature_id_by_feature_name(feature_name):
    find_value_in_list_of_dictionary("name", feature_name, config("list_of_features"))
    for feature in config("list_of_features"):
        if feature_name == feature["name"]:
            return feature["id"]
        
def execute_vidcall_1():
    st.header(lockey("header_notes"))
    st.markdown(
        """
        1. Input one of these value for blacklist_type:
        - device-type
        - nik
        - phone-number
        2. Input the value to be blacklisted in column blacklist_value
        - For device type, check in table provisioning.user_registration
        - For phone number, don't forget to use the prefix country code (ex: "6281234567")
        3. Input one of these value for status:
        - BLACKLIST
        - RELEASE
        """
    )

    st.divider()

    blacklist_data = pd.DataFrame(
        {
            "blacklist_type": pd.Series(dtype="string"),
            "blacklist_value": pd.Series(dtype="string"),
            "status": pd.Series(dtype="string")
        }
    )

    blacklist_data = st.data_editor(
        data = blacklist_data,
        num_rows = "dynamic",
        column_config = {
            "blacklist_type": st.column_config.TextColumn(
                lockey("query_label_blacklist_type_column"),
                required = True
            ),
            "blacklist_value": st.column_config.TextColumn(
                lockey("query_label_blacklist_value_column"),
                required = True
            ),
            "status": st.column_config.SelectboxColumn(
                lockey("query_label_status_column"),
                options = ["BLACKLIST", "RELEASE"],
                required = True
            )
        }     
    )
    
    blacklist_value = ", ".join(f"'{value}'" for value in blacklist_data["blacklist_value"])
    query_select = find_value_in_list_of_dictionary.execute("id", "vidcall-1", config("query"))["query_select"]
    query_select = query_select.format(blacklist_value = blacklist_value)
    
    query_execute = find_value_in_list_of_dictionary.execute("id", "vidcall-1", config("query"))["query_execute"]
    blacklist_data["query"] = blacklist_data.apply(lambda row: generate_execute_query_vidcall_1(row, query_execute), axis = 1)
    query_execute = " \n\n".join(blacklist_data["query"])
    
    all_query = f"--SELECT--\n{query_select}\n\n--EXECUTE--\n{query_execute}"
    all_query = all_query.encode("utf-8")
    file_name = find_value_in_list_of_dictionary.execute("id", "vidcall-1", config("list_of_features"))["name"] + ".sql"

    st.download_button(
        label = lockey("query_button_download"),
        data = all_query,
        file_name = file_name,
        mime="application/sql"
    )

def generate_execute_query_vidcall_1(row, query):
    blacklisted_id = uuid.uuid4()
    blacklist_type = row["blacklist_type"]
    blacklist_value = row["blacklist_value"]
    status = 0 if row["status"] == "BLACKLIST" else 0
    return query.format(
        blacklisted_id = blacklisted_id,
        blacklist_type = blacklist_type,
        blacklist_value = blacklist_value,
        status = status
    )