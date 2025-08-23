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
    elif st.session_state.feature != feature:
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
            
            default_values = [None for column in columns_name]
            data = [dict(zip(columns_name, default_values))]
            column_config = dict(zip(columns_name, column_config))

            st.session_state.data_configs[f"data-{table.id}"] = {
                "data": data,
                "column_config": column_config,
                "preview": ""
            }
    
    for table in tables_to_be_executed.itertuples(index=True):
        if f"invalid_input_table-{table.id}" not in st.session_state:
            st.session_state[f"invalid_input_table-{table.id}"] = False
        
        with st.form(key = "form-" + table.id, clear_on_submit = False):
            # Show tables
            st.write(lockey("query_label_table_name") + table.table_name)

            st.session_state.data_configs[f"data-{table.id}"]["data"] = st.data_editor(
                data = st.session_state.data_configs[f"data-{table.id}"]["data"],
                column_config = st.session_state.data_configs[f"data-{table.id}"]["column_config"],
                num_rows = "dynamic",
                key = f"data-{table.id}"
            )
            
            # Check if download button is disabled
            if st.session_state.data_configs[f"data-{table.id}"]["preview"] == "":
                is_download_button_disabled = True
            else:
                is_download_button_disabled = False

            # Show query preview
            st.session_state.data_configs[f"data-{table.id}"]["preview"] = st.text_area(
                label = lockey("query_label_preview"),
                value = st.session_state.data_configs[f"data-{table.id}"]["preview"],
                disabled = is_download_button_disabled,
                height = 200
            )

            # Create buttpn columns
            button_columns = st.columns(spec = 4, gap = "small")

            # Create preview button
            with button_columns[0]:
                if st.form_submit_button(label = lockey("query_label_generate_query"), use_container_width = True):
                    # Convert data into data frame
                    data = pd.DataFrame(st.session_state.data_configs[f"data-{table.id}"]["data"])

                    # Check if input is invalid
                    if not is_input_valid(data, st.session_state.data_configs[f"data-{table.id}"]["column_config"]):
                        st.session_state[f"invalid_input_table-{table.id}"] = True
                        st.rerun()

                    st.session_state.data_configs[f"data-{table.id}"]["preview"] = generate_query(
                        data = data,
                        columns_name = data.columns,
                        query_select = table.query_select,
                        query_execute = table.query_execute
                    )
                    st.rerun()

            # Create download button
            with button_columns[1]:
                if st.form_submit_button(label = lockey("query_button_confirmation"), use_container_width = True, disabled = is_download_button_disabled):
                    download_query(
                        query = st.session_state.data_configs[f"data-{table.id}"]["preview"],
                        filename = feature_name + " - " + table.table_name + ".sql"
                    )
        
        # Check if input is invalid
        if st.session_state[f"invalid_input_table-{table.id}"] == True:
            st.error(lockey("query_label_invalid_input"))
            st.session_state[f"invalid_input_table-{table.id}"] = False
        

def define_column_config(column):
    # Check if column[is_required] is exist (backward compatibility)
    if "is_required" in column:
        is_required = column["is_required"]
    else:
        is_required = True
    
    # Check if the column contains LOV
    if len(column["lov"]) == 0:
        return st.column_config.TextColumn(
            label = column["name"],
            required = is_required
            )
    else:
        return st.column_config.SelectboxColumn(
            label = column["name"],
            options = column["lov"],
            required = is_required
        )

def is_input_valid(data, column_config):
    for column_name, configuration in column_config.items():
        if (configuration["required"] == True) and (data[column_name].isnull().any()):
            return False
    
    return True

def generate_execute_query(row, query, columns_name):
    generated_uuid = str(uuid.uuid4())
    query = query.replace(f"{{uuid}}", generated_uuid)

    for column in columns_name:
        if (row[column] in (None, "")) or (str(row[column]).lower() == "null"):
            query = query.replace(f"'{{{column}}}'", "NULL")
            query = query.replace(f"{{{column}}}", "NULL")
        else:
            query = query.replace(f"{{{column}}}", str(row[column]))

    return query

def generate_query(data, columns_name, query_select, query_execute):
    data_select = data.astype(str).apply(lambda col: ", ".join(f"'{val}'" for val in col)).to_dict()

    for column in columns_name:
        query_select = query_select.replace(f"{{{column}}}", data_select[column])
    
    sql_keywords = ["select", "update", "merge", "delete", "insert"]
    if any(keyword.lower() in query_execute.lower() for keyword in sql_keywords):
        data["query"] = data.apply(lambda row: generate_execute_query(row, query_execute, columns_name), axis = 1)
        query_execute = " \n\n".join(data["query"])
    
    all_query = f"SET DEFINE OFF;\n\n--EXECUTE--\n{query_execute}\n\n--SELECT--\n{query_select}"

    return all_query

@st.dialog(title = "Confirmation")
def download_query(query, filename):
    st.write(lockey("query_description_download_confirmation"))

    if st.download_button(
        label = lockey("query_button_download"),
        data = query,
        file_name = filename,
        mime="text/plain"):
        st.rerun()