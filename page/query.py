import streamlit as st
import pandas as pd
import uuid
from common_handling import set_lockey
from common_handling import find_config
from common_handling import find_value_in_dataframe
from common_handling import is_password_valid

lockey = set_lockey.execute
config = find_config.execute

def app():
    if not is_password_valid.execute():
        return {}
    
    features = pd.DataFrame(config("features"))
    tables = pd.DataFrame(config("tables"))

    if (len(features) == 0) and (len(tables) == 0):
        st.error(lockey("common_error_empty_data"))
        return {}

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

            downloaded = st.form_submit_button(lockey("query_button_confirmation"))
            
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

@st.dialog(title = "Confirmation")
def download_query(data, feature_name, table_name, columns_name, query_select, query_execute):
    data_select = data.astype(str).apply(lambda col: ", ".join(f"'{val}'" for val in col)).to_dict()

    for column in columns_name:
        query_select = query_select.replace(f"{{{column}}}", data_select[column])
    
    data["query"] = data.apply(lambda row: generate_execute_query(row, query_execute, columns_name), axis = 1)
    query_execute = " \n\n".join(data["query"])
    
    all_query = f"--SELECT--\n{query_select}\n\n--EXECUTE--\n{query_execute}"
    filename = feature_name + " - " + table_name + ".sql"

    st.write(lockey("query_description_download_confirmation"))

    if st.download_button(
        label = lockey("query_button_download"),
        data = all_query,
        file_name = filename,
        mime="text/plain"):
        st.rerun()

def generate_execute_query(row, query, columns_name):
    generated_uuid = str(uuid.uuid4())
    query = query.replace(f"{{uuid}}", generated_uuid)

    for column in columns_name:
        query = query.replace(f"{{{column}}}", str(row[column]))

    return query