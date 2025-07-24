import streamlit as st
import pandas as pd
import uuid
from common_handling import set_lockey
from common_handling import find_config
from common_handling import find_value_in_dataframe
from common_handling import is_password_valid
from common_handling import is_config_exist

lockey = set_lockey.execute
config = find_config.execute

def app():
    if not is_password_valid.execute():
        return {}
    
    if not is_config_exist.execute():
        return {}
    
    features = pd.DataFrame(config("features"))
    tables = pd.DataFrame(config("tables"))

    feature = st.selectbox(
        label = lockey("query_label_feature"),
        options = features["name"].sort_values(),
        index = None
        )
    
    if feature is None:
        return {}
    
    if feature not in features["name"].values:
        st.error(lockey("query_error_feature_not_exist"))
        return {}
        
    if "feature" not in st.session_state:
        st.session_state.feature = feature
    elif st.session_state != feature:
        del st.session_state.data_configs
        st.session_state.feature = feature

    feature_id = find_value_in_dataframe.execute(
        data = features,
        search_column = "id",
        reference_column = "name",
        search_value = feature
    ).iloc[0]
    
    execute_feature(features, tables, feature_id, feature)

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
    st.markdown(f"""{notes}""")

    st.divider()

    if "data_configs" not in st.session_state:
        st.session_state.data_configs = dict()
        for table in tables_to_be_executed.itertuples(index=True):
            columns = pd.DataFrame(table.columns)
            columns["column_config"] = columns.apply(lambda column: define_column_config(column), axis = 1)
            columns_name = columns["name"].tolist()
            column_config = columns["column_config"].tolist()
            
            data = pd.DataFrame(
                columns = columns_name,
                dtype = "object"
            )
            column_config = dict(zip(columns_name, column_config))

            st.session_state.data_configs[f"data-{table.id}"] = {
                "data": data,
                "column_config": column_config
            }

    for table in tables_to_be_executed.itertuples(index=True):
        with st.form(key = "form-" + table.id, clear_on_submit = False):
            st.write(lockey("query_label_table_name") + table.table_name)

            st.session_state.data_configs[f"data-{table.id}"]["data"] = st.data_editor(
                data = st.session_state.data_configs[f"data-{table.id}"]["data"],
                num_rows = "dynamic",
                column_config = st.session_state.data_configs[f"data-{table.id}"]["column_config"],
                key = f"data-{table.id}"
            )

            downloaded = st.form_submit_button(lockey("query_button_confirmation"))
            
        if downloaded:
            download_query(st.session_state.data_configs[f"data-{table.id}"]["data"],
                            feature_name,
                            table.table_name,
                            st.session_state.data_configs[f"data-{table.id}"]["data"].columns,
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

@st.dialog(title = "Confirmation")
def download_query(data, feature_name, table_name, columns_name, query_select, query_execute):
    data_select = data.astype(str).apply(lambda col: ", ".join(f"'{val}'" for val in col)).to_dict()

    for column in columns_name:
        query_select = query_select.replace(f"{{{column}}}", data_select[column])
    
    sql_keywords = ["select", "update", "merge", "delete", "insert"]
    if any(keyword.lower() in query_execute.lower() for keyword in sql_keywords):
        data["query"] = data.apply(lambda row: generate_execute_query(row, query_execute, columns_name), axis = 1)
        query_execute = " \n\n".join(data["query"])
    
    all_query = f"--SELECT--\n{query_select}\n\n--EXECUTE--\n{query_execute}"
    filename = feature_name + " - " + table_name + ".sql"

    st.write(lockey("query_description_download_confirmation"))

    download_button = st.download_button(
        label = lockey("query_button_download"),
        data = all_query,
        file_name = filename,
        mime="text/plain"
    )

    if download_button:
        st.rerun()

def generate_execute_query(row, query, columns_name):
    generated_uuid = str(uuid.uuid4())
    query = query.replace(f"{{uuid}}", generated_uuid)

    for column in columns_name:
        query = query.replace(f"{{{column}}}", str(row[column]))

    return query