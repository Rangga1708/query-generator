import streamlit as st
import pandas as pd
import uuid
import base64
import streamlit.components.v1 as components
from common_handling import set_lockey, find_config, find_value_in_list_of_dictionary, find_value_in_dataframe

lockey = set_lockey.execute
config = find_config.execute

def app():
    features = pd.DataFrame(config("features"))
    tables = pd.DataFrame(config("tables"))

    feature = st.selectbox(
        label = lockey("query_label_feature"),
        options = features["name"],
        index = None
        )
    
    if feature is None:
        return {}
    elif feature is not None and feature not in features["name"].values:
        st.error(lockey("query_error_feature_not_exist"))
        return {}

    feature_id = find_value_in_dataframe.execute(
        data = features,
        search_column = "id",
        reference_column = "name",
        search_value = feature
    ).iloc[0]
    
    execute_feature(features, tables, feature_id, feature)
    # if feature_id == "vidcall-1":
        # execute_vidcall_1()
                
# def find_feature_id_by_feature_name(feature_name):
#     find_value_in_list_of_dictionary("name", feature_name, config("list_of_features"))
#     for feature in config("list_of_features"):
#         if feature_name == feature["name"]:
#             return feature["id"]

def execute_feature(features, tables, feature_id, feature_name):
    notes = find_value_in_dataframe.execute(
        data = features,
        search_column = "notes",
        reference_column = "id",
        search_value = feature_id
    ).iloc[0]

    tables_to_be_executed = find_value_in_dataframe.execute(
        data = tables,
        reference_column = "feature_id",
        search_value = feature_id
    )

    st.header(lockey("header_notes"))
    st.markdown(
        f"""
        {notes}
        """
    )

    st.divider()

    for table in tables_to_be_executed.itertuples(index=True):
        with st.form(key = "form-" + table.id, clear_on_submit = False):
            st.write(lockey("query_label_table_name") + table.table_name)
            
            columns = pd.DataFrame(table.columns)
            columns["column_config"] = columns.apply(lambda column: define_column_config(column), axis = 1)
            columns_name = columns["name"].tolist()
            columns_type = [pd.Series(dtype="string") for i in range(len(columns_name))]
            column_config = columns["column_config"].tolist()

            data = pd.DataFrame(dict(zip(columns_name, columns_type)))
            column_config = dict(zip(columns_name, column_config))

            data = st.data_editor(
                data = data,
                num_rows = "dynamic",
                column_config = column_config,
                key = "data-" + table.id
            )

            downloaded = st.form_submit_button(lockey("query_button_download"))
            
            if downloaded:
                download_query(data,
                               feature_name,
                               table.table_name,
                               columns_name,
                               table.query_select,
                               table.query_execute)

def define_column_config(column):
    if len(column["lov"]) == 0:
        return st.column_config.TextColumn(
            label = column["name"],
            required = True
            )
    else:
        return st.column_config.SelectboxColumn(
            label = column["name"],
            options = column["lov"],
            required = True
        )
    
def download_query(data, feature_name, table_name, columns_name, query_select, query_execute):
    data_select = data.astype(str).apply(lambda col: ", ".join(f"'{val}'" for val in col)).to_dict()

    for column in columns_name:
        query_select = query_select.replace(f"{{{column}}}", data_select[column])
    
    data["query"] = data.apply(lambda row: generate_execute_query(row, query_execute, columns_name), axis = 1)
    query_execute = " \n\n".join(data["query"])
    
    all_query = f"--SELECT--\n{query_select}\n\n--EXECUTE--\n{query_execute}"
    filename = feature_name + " - " + table_name + ".sql"

    components.html(
        download_button(all_query, filename),
        height=0,
    )

def generate_execute_query(row, query, columns_name):
    generated_uuid = str(uuid.uuid4())
    query = query.replace(f"{{uuid}}", generated_uuid)

    for column in columns_name:
        query = query.replace(f"{{{column}}}", str(row[column]))

    return query

def download_button(object_to_download, download_filename):
    if isinstance(object_to_download, str):
        b64 = base64.b64encode(object_to_download.encode()).decode()
    else:
        b64 = base64.b64encode(object_to_download).decode()

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:application/octet-stream;base64,{b64}" download="{download_filename}">')[0].click()
    </script>
    </head>
    </html>
    """
    return dl_link

# def execute_vidcall_1():
#     st.header(lockey("header_notes"))
#     st.markdown(
#         """
#         1. Input one of these value for blacklist_type:
#         - device-type
#         - nik
#         - phone-number
#         2. Input the value to be blacklisted in column blacklist_value
#         - For device type, check in table provisioning.user_registration
#         - For phone number, don't forget to use the prefix country code (ex: "6281234567")
#         3. Input one of these value for status:
#         - BLACKLIST
#         - RELEASE
#         """
#     )

#     st.divider()

#     blacklist_data = pd.DataFrame(
#         {
#             "blacklist_type": pd.Series(dtype="string"),
#             "blacklist_value": pd.Series(dtype="string"),
#             "status": pd.Series(dtype="string")
#         }
#     )

#     blacklist_data = st.data_editor(
#         data = blacklist_data,
#         num_rows = "dynamic",
#         column_config = {
#             "blacklist_type": st.column_config.TextColumn(
#                 lockey("query_label_blacklist_type_column"),
#                 required = True
#             ),
#             "blacklist_value": st.column_config.TextColumn(
#                 lockey("query_label_blacklist_value_column"),
#                 required = True
#             ),
#             "status": st.column_config.SelectboxColumn(
#                 lockey("query_label_status_column"),
#                 options = ["BLACKLIST", "RELEASE"],
#                 required = True
#             )
#         }     
#     )
    
#     blacklist_value = ", ".join(f"'{value}'" for value in blacklist_data["blacklist_value"])
#     query_select = find_value_in_list_of_dictionary.execute("id", "vidcall-1", config("query"))["query_select"]
#     query_select = query_select.format(blacklist_value = blacklist_value)
    
#     query_execute = find_value_in_list_of_dictionary.execute("id", "vidcall-1", config("query"))["query_execute"]
#     blacklist_data["query"] = blacklist_data.apply(lambda row: generate_execute_query_vidcall_1(row, query_execute), axis = 1)
#     query_execute = " \n\n".join(blacklist_data["query"])
    
#     all_query = f"--SELECT--\n{query_select}\n\n--EXECUTE--\n{query_execute}"
#     all_query = all_query.encode("utf-8")
#     file_name = find_value_in_list_of_dictionary.execute("id", "vidcall-1", config("list_of_features"))["name"] + ".sql"

#     st.download_button(
#         label = lockey("query_button_download"),
#         data = all_query,
#         file_name = file_name,
#         mime="application/sql"
#     )

# def generate_execute_query_vidcall_1(row, query):
#     blacklisted_id = uuid.uuid4()
#     blacklist_type = row["blacklist_type"]
#     blacklist_value = row["blacklist_value"]
#     status = 0 if row["status"] == "BLACKLIST" else 0
#     return query.format(
#         blacklisted_id = blacklisted_id,
#         blacklist_type = blacklist_type,
#         blacklist_value = blacklist_value,
#         status = status
#     )