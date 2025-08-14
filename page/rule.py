import json
import uuid
import copy
import streamlit as st
import pandas as pd
from common_handling import set_lockey
from common_handling import find_config
from common_handling import find_value_in_dataframe
from common_handling import is_password_valid
from common_handling import is_config_exist
from api import put_v3_update_feature
from api import post_v3_add_feature

lockey = set_lockey.execute
config = find_config.execute

def app():
   if not is_password_valid.execute():
      return {}
   
   tabs = st.tabs([
      lockey("rule_title_import_feature"),
      lockey("rule_title_insert_feature"),
      lockey("rule_title_update_feature")
   ])

   with tabs[0]:
      import_feature()
   
   with tabs[1]:
      add_new_feature()

   with tabs[2]:
      update_feature()

def import_feature():
   if "show_import_success" not in st.session_state:
      st.session_state.show_import_success = False

   file = st.file_uploader(
      label = lockey("rule_label_import_feature"),
      type = "json"
   )

   if file is not None:
      try:
         file = json.loads(file.read())
      except:
         st.error(lockey("rule_label_invalid_file_format"))
         return {}
      
      if not is_file_valid(file):
         st.error(lockey("rule_label_invalid_file_format"))
         return {}

      features = pd.DataFrame(file["features"])
      tables = pd.DataFrame(file["tables"])
      features_tables = pd.merge(features, tables, left_on = "id", right_on = "feature_id", how = "inner")

      st.dataframe(
         data = features_tables[["name", "table_name"]],
         column_config = {
            "name": "Feature Name",
            "table_name": "Table Name"
         }
      )

      save_button = st.button(
         label = lockey("rule_button_save_imported_feature"),
         type = "primary"
      )

      if save_button:
         st.session_state.config = file
         st.session_state.show_import_success = True
         st.rerun()
   
   else:
      if is_config_exist.execute():
         features = pd.DataFrame(config("features"))
         tables = pd.DataFrame(config("tables"))
         features_tables = pd.merge(features, tables, left_on = "id", right_on = "feature_id", how = "inner")

         st.dataframe(
            data = features_tables[["name", "table_name"]],
            column_config = {
               "name": "Feature Name",
               "table_name": "Table Name"
            }
         )

         features_json = json.dumps({
            "features": config("features"),
            "tables": config("tables")
         },
         indent = 2)
            
         st.download_button(
            label = lockey("query_button_download"),
            data = features_json,
            file_name = "rule.json",
            mime="text/plain",
            type = "primary"
         )
   
   if st.session_state.show_import_success:
      st.success(lockey("rule_label_feature_import_success"))
      st.session_state.show_import_success = False
   
def add_new_feature():
   if "new_tables" not in st.session_state:
      st.session_state.new_tables = [new_table()]
   
   if "response_post_add_feature" not in st.session_state:
      st.session_state.response_post_add_feature = None

   with st.form(key = "Form New Feature", border = False, clear_on_submit = False):
      with st.container(border = True):
         feature = {
            "name": st.text_input(
               label = lockey("rule_label_feature_name"),
               placeholder = lockey("rule_placeholder_feature_name")),
            "notes": st.text_area(
               label = lockey("rule_label_feature_notes"),
               height = 100)
         }

      for i in range (len(st.session_state.new_tables)):
         with st.container(border = True):
            try:
               st.session_state.new_tables[i]["table_name"] = st.text_input(
                     label = lockey("rule_label_table_name"),
                     value = st.session_state.new_tables[i]["table_name"],
                     key = f"table_name - {i}")
               st.session_state.new_tables[i]["query_select"] = st.text_area(
                     label = lockey("rule_label_query_select"),
                     value = st.session_state.new_tables[i]["query_select"],
                     height = 100,
                     key = f"query_select - {i}")
               st.session_state.new_tables[i]["query_execute"] = st.text_area(
                     label = lockey("rule_label_query_execute"),
                     value = st.session_state.new_tables[i]["query_execute"],
                     height = 200,
                     key = f"query_execute - {i}")
               st.write(lockey("rule_label_columns"))
               st.session_state.new_tables[i]["columns"] = st.data_editor(
                     data = st.session_state.new_tables[i]["columns"],
                     column_config = column_config(),
                     num_rows = "dynamic",
                     key = f"columns - {i}")
            except:
               st.session_state.response_post_add_feature = {
                  "status": "30001",
                  "message": lockey("rule_label_invalid_input")
               }

      button_columns = st.columns(spec = 4, gap = "small")
      
      if len(st.session_state.new_tables) == 1:
         is_delete_button_disabled = True
      else:
         is_delete_button_disabled = False

      with button_columns[0]:
         if st.form_submit_button(label = lockey("rule_button_add_new_table"), use_container_width = True):
            st.session_state.new_tables.append(new_table())
            st.rerun()
      
      with button_columns[1]:
         if st.form_submit_button(label = lockey("rule_button_delete_new_table"), use_container_width = True, disabled = is_delete_button_disabled):
            st.session_state.new_tables.pop()
            st.rerun()
      
      with button_columns[2]:
         if st.form_submit_button(label = lockey("rule_button_clear_input"), use_container_width = True, disabled = is_delete_button_disabled):
            st.session_state.new_tables = [new_table()]
            st.rerun()

      with button_columns[3]:
         if st.form_submit_button(label = lockey("rule_button_submit_feature"), use_container_width = True, type = "primary"):
            request = {
               "feature": feature,
               "tables": copy.deepcopy(st.session_state.new_tables)
            }

            st.session_state.response_post_add_feature = post_v3_add_feature.execute(request)
            st.rerun()

   if st.session_state.response_post_add_feature != None:
      if st.session_state.response_post_add_feature["status"] == "200":
         st.success(st.session_state.response_post_add_feature["message"])
         del st.session_state.new_tables
         st.session_state.response_post_add_feature = None
      else:
         st.error(st.session_state.response_post_add_feature["message"])
         st.session_state.response_post_add_feature = None

def update_feature():
   if not is_config_exist.execute():
      return {}

   if "update_feature_name" not in st.session_state:
      st.session_state.update_feature_name = ""
   
   features = pd.DataFrame(config("features"))
   tables = pd.DataFrame(config("tables"))
   
   feature = st.selectbox(
      label = lockey("rule_label_feature"),
      options = features.sort_values(by = "name")["name"],
      index = None,
      key = "update_feature"
   )

   if feature is None:
      return {}
   elif feature is not None and feature not in features["name"].values:
      st.error(lockey("rule_error_feature_not_exist"))
      return {}

   feature_info = find_value_in_dataframe.execute(
      data = features,
      search_value = feature,
      reference_column = "name"
   ).iloc[0]

   if feature != st.session_state.update_feature_name:
      st.session_state.update_feature_name = feature
      st.session_state.update_tables = find_value_in_dataframe.execute(
         data = tables,
         search_value = feature_info["id"],
         reference_column = "feature_id"
      ).to_dict(orient = "records")

      # Convert lov from list into string split by pipe
      for table in st.session_state.update_tables:
         for i in range(len(table["columns"])):
            if len(table["columns"][i]["lov"]) != 0:
               table["columns"][i]["lov"] = "|".join(table["columns"][i]["lov"])
            else:
               table["columns"][i]["lov"] = None
   
   if "response_put_update_feature" not in st.session_state:
      st.session_state.response_put_update_feature = None

   with st.form(key = "Form Update Feature", border = False, clear_on_submit = False):
      with st.container(border = True):
         feature = {
            "id": feature_info["id"],
            "name": st.text_input(
               label = lockey("rule_label_feature_name"),
               placeholder = lockey("rule_placeholder_feature_name"),
               value = feature_info["name"]),
            "notes": st.text_area(
               label = lockey("rule_label_feature_notes",),
               value = feature_info["notes"])
         }

      for i in range (len(st.session_state.update_tables)):
         with st.container(border = True):
            try:
               st.session_state.update_tables[i]["table_name"] = st.text_input(
                     label = lockey("rule_label_table_name"),
                     value = st.session_state.update_tables[i]["table_name"],
                     key = f"table_name_update - {i}")
               st.session_state.update_tables[i]["query_select"] = st.text_area(
                     label = lockey("rule_label_query_select"),
                     value = st.session_state.update_tables[i]["query_select"],
                     height = 100,
                     key = f"query_select_update - {i}")
               st.session_state.update_tables[i]["query_execute"] = st.text_area(
                     label = lockey("rule_label_query_execute"),
                     value = st.session_state.update_tables[i]["query_execute"],
                     height = 200,
                     key = f"query_execute_update - {i}")
               st.write(lockey("rule_label_columns"))
               st.session_state.update_tables[i]["columns"] = st.data_editor(
                     data = st.session_state.update_tables[i]["columns"],
                     column_config = column_config(),
                     num_rows = "dynamic",
                     key = f"columns_update - {i}")
            except:
               st.session_state.response_put_update_feature = {
                  "status": "30001",
                  "message": lockey("rule_label_invalid_input")
               }

      button_columns = st.columns(spec = 4, gap = "small")
      
      if len(st.session_state.update_tables) == 1:
         is_delete_button_disabled = True
      else:
         is_delete_button_disabled = False

      with button_columns[0]:
         if st.form_submit_button(label = lockey("rule_button_add_new_table"), use_container_width = True):
            st.session_state.update_tables.append(new_table(feature_info["id"]))
            st.rerun()
      
      with button_columns[1]:
         if st.form_submit_button(label = lockey("rule_button_delete_new_table"), use_container_width = True, disabled = is_delete_button_disabled):
            st.session_state.update_tables.pop()
            st.rerun()
      
      with button_columns[2]:
         if st.form_submit_button(label = lockey("rule_button_clear_input"), use_container_width = True, disabled = is_delete_button_disabled):
            st.session_state.update_tables = [new_table(feature_info["id"])]
            st.rerun()

      with button_columns[3]:
         if st.form_submit_button(label = lockey("rule_button_submit_feature"), use_container_width = True, type = "primary"):
            request = {
               "feature": feature,
               "tables": copy.deepcopy(st.session_state.update_tables)
            }

            st.session_state.response_put_update_feature = put_v3_update_feature.execute(request)
            st.rerun()

   if st.session_state.response_put_update_feature != None:
      if st.session_state.response_put_update_feature["status"] == "200":
         st.success(st.session_state.response_put_update_feature["message"])
         del st.session_state.new_tables
         st.session_state.response_put_update_feature = None
      else:
         st.error(st.session_state.response_put_update_feature["message"])
         st.session_state.response_put_update_feature = None

def is_file_valid(file):
   if ("features" not in file) or ("tables" not in file):
      return False
      
   if (type(file["features"]) != type([])) or (type(file["tables"]) != type([])):
      return False

   if (len(file["features"]) == 0) or (len(file["tables"]) == 0):
      return False
            
   return True

def new_table(feature_id = None):
   if feature_id == None:
      return {
         "table_name": "",
         "query_select": "",
         "query_execute": "",
         "columns": [{
            "name": None,
            "lov": None,
            "is_required": True
            }]
      }
   else:
      return {
         "id": str(uuid.uuid4()),
         "feature_id": feature_id,
         "table_name": "",
         "query_select": "",
         "query_execute": "",
         "columns": [{
            "name": None,
            "lov": None,
            "is_required": True
            }]
      }

def column_config():
   return {
      "name": st.column_config.TextColumn(
            label = lockey("rule_label_column_name"),
            required = True
            ),
      "lov": st.column_config.TextColumn(
            label = lockey("rule_label_lov"),
            required = False,
            help = lockey("rule_label_lov_tooltip")
            ),
      "is_required": st.column_config.CheckboxColumn(
            label = lockey("rule_label_is_required"),
            required = True,
            default = True
            )
   }