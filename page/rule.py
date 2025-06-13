import streamlit as st
import pandas as pd
import json
from datetime import datetime as dt
from common_handling import set_lockey, find_config, find_value_in_dataframe
from api import put_v1_update_feature

lockey = set_lockey.execute
config = find_config.execute

def app():
   features = pd.DataFrame(config("features"))
   tables = pd.DataFrame(config("tables"))

   tabs = st.tabs([
      lockey("rule_title_update_feature"),
      lockey("rule_title_insert_feature"),
      lockey("rule_title_insert_table")
   ])

   with tabs[0]:
      update_feature(features, tables)

   # with tabs[1]:
   #    with st.form(key = "Form Feature"):
   #       st.write(lockey("rule_label_features"))
   #       feature_id = st.text_input(
   #          label = lockey("rule_label_feature_id"),
   #          placeholder = lockey("rule_placeholder_feature_id"))
   #       feature_name = st.text_input(
   #          label = lockey("rule_label_feature_name"),
   #          placeholder = lockey("rule_placeholder_feature_name"))
   #       notes = st.text_area(label = lockey("rule_label_feature_notes"))
         
   #       submitted = st.form_submit_button(
   #          label = lockey("rule_button_submit_feature")
   #       )

   #        if submitted:
   #           st.write(notes)

def update_feature(features, tables): 
   feature = st.selectbox(
      label = lockey("rule_label_feature"),
      options = features.sort_values(by = "name")["name"],
      index = None
      )

   if "clean_field" not in st.session_state:
      st.session_state.clean_field = False

   if (feature is None) or (st.session_state.clean_field):
      return {}
   elif feature is not None and feature not in features["name"].values:
      st.error(lockey("rule_error_feature_not_exist"))
      return {}

   with st.form(key = "Update Feature", border = True):
      feature_info = find_value_in_dataframe.execute(
         data = features,
         search_value = feature,
         reference_column = "name"
      ).iloc[0]

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
            "columns": json.loads(st.text_area(
               label = lockey("rule_label_columns"),
               value = json.dumps(table.columns, indent = 2)
            )),
            "updated_time": dt.now().strftime("%Y-%m-%d %H:%M:%S")
         })

         st.divider()

      if st.form_submit_button(label = lockey("rule_button_update_feature")):
         request = {
            "feature": feature_info_updated,
            "tables": feature_tables_updated
         }

         try:
            put_v1_update_feature.execute(request)
            st.success(lockey("rule_label_update_success"))
            st.session_state.clean_fields = True
            st.rerun()
         except:
            st.error(lockey("rule_label_update_failed"))