import streamlit as st
import pandas as pd
import json
from datetime import datetime as dt
from common_handling import set_lockey
from common_handling import find_config
from common_handling import find_value_in_dataframe
from common_handling import is_password_valid
from api import put_v1_update_feature
from api import post_v1_add_feature
from api import post_v1_add_table_rule

lockey = set_lockey.execute
config = find_config.execute

def app():
   if not is_password_valid.execute():
        return {}

   features = pd.DataFrame(config("features"))
   tables = pd.DataFrame(config("tables"))

   tabs = st.tabs([
      lockey("rule_title_update_feature"),
      lockey("rule_title_insert_feature"),
      lockey("rule_title_insert_table")
   ])

   with tabs[0]:
      update_feature(features, tables)

   with tabs[1]:
      add_new_feature(features)
   
   with tabs[2]:
      add_new_table_rule(features, tables)

def update_feature(features, tables): 
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

   with st.form(key = "Update Feature", border = True):
      feature_info_updated = {
         "id": feature_info["id"],
         "name": st.text_input(
            label = lockey("rule_label_feature_name"),
            value = feature_info["name"]
         ),
         "notes": st.text_area(
            label = lockey("rule_label_feature_notes"),
            value = feature_info["notes"]
         ),
         "updated_time": dt.now().strftime("%Y-%m-%d %H:%M:%S")
      }

      st.divider()

      feature_tables = find_value_in_dataframe.execute(
            data = tables,
            search_value = feature_info["id"],
            reference_column = "feature_id"
         )
      
      feature_tables_updated = []
      for table in feature_tables.itertuples(index=True):
         feature_tables_updated.append({
            "id": table.id,
            "feature_id": feature_info["id"],
            "table_name": st.text_input(
               label = lockey("rule_label_table_name"),
               value = table.table_name
            ),
            "query_select": st.text_area(
               label = lockey("rule_label_query_select"),
               value = table.query_select
            ),
            "query_execute": st.text_area(
               label = lockey("rule_label_query_execute") ,
               value = table.query_execute
            ),
            "columns": st.text_area(
               label = lockey("rule_label_columns"),
               value = json.dumps(table.columns, indent = 2)
            ),
            "updated_time": dt.now().strftime("%Y-%m-%d %H:%M:%S")
         })

         st.divider()

      if st.form_submit_button(label = lockey("rule_button_update_feature")):
         request = {
            "feature": feature_info_updated,
            "tables": feature_tables_updated
         }

         response = put_v1_update_feature.execute(request)

         if response["status"] == "200":
            st.success(response["message"])
         else:
            st.error(response["message"])

def add_new_feature(features):
   with st.form(key = "Form New Feature", border = True):
      request = {
         "name": st.text_input(
            label = lockey("rule_label_feature_name"),
            placeholder = lockey("rule_placeholder_feature_name")),
         "notes": st.text_area(label = lockey("rule_label_feature_notes"))
      }
      
      if st.form_submit_button(label = lockey("rule_button_submit_feature")):
         response = post_v1_add_feature.execute(request)

         if response["status"] == "200":
            st.success(response["message"])
         else:
            st.error(response["message"])

def add_new_table_rule(features, tables):
   feature = st.selectbox(
      label = lockey("rule_label_feature"),
      options = features.sort_values(by = "name")["name"],
      index = None,
      key = "add new table rule"
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
   
   with st.form(key = "Form New Table Rule", border = True):
      request = {
         "feature_id": feature_info["id"],
         "table_name": st.text_input(label = lockey("rule_label_table_name")),
         "query_select": st.text_area(label = lockey("rule_label_query_select")),
         "query_execute": st.text_area(label = lockey("rule_label_query_execute")),
         "columns": st.text_area(
            label = lockey("rule_label_columns"),
            value = json.dumps([
               {
                  "lov":[],
                  "name": ""
               }
            ], indent = 2))
      }

      if st.form_submit_button(label = lockey("rule_button_submit_feature")):
         response = post_v1_add_table_rule.execute(request)

         if response["status"] == "200":
            st.success(response["message"])
         else:
            st.error(response["message"])