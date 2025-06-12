import streamlit as st
import pandas as pd
from common_handling import set_lockey, find_config, find_value_in_dataframe

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
      update_feature()

   with tabs[1]:
      with st.form(key = "Form Feature"):
         st.write(lockey("rule_label_features"))
         feature_id = st.text_input(
            label = lockey("rule_label_feature_id"),
            placeholder = lockey("rule_placeholder_feature_id"))
         feature_name = st.text_input(
            label = lockey("rule_label_feature_name"),
            placeholder = lockey("rule_placeholder_feature_name"))
         notes = st.text_area(label = lockey("rule_label_feature_notes"))
         
         submitted = st.form_submit_button(
            label = lockey("rule_button_submit_feature")
         )

          if submitted:
             st.write(notes)

def update_feature(features, tables): 
   with st.columns(spec = 1, border = True):
      feature = st.selectbox(
         label = lockey("rule_label_feature"),
         options = features.sort_values(by = "name")["name"],
         index = None
         )

   if feature is None:
      return {}
   elif feature is not None and feature not in features["name"].values:
      st.error(lockey("rule_error_feature_not_exist"))
      return {}

   with st.form(key = "Update Feature"):
      feature_rule = find_value_in_dataframe(
         data = features,
         search_value = feature,
         reference_column = "name"
      )

      feature_name = st.text_input(
         label = lockey("rule_label_feature_name"),
         value = feature
      )

      notes = st.text_area(
         label = lockey("rule_label_feature_notes"),
         value = feature_rule["notes"]
      )

   st.divider()

   feature_tables = find_value_in_dataframe(
         data = tables,
         search_value = feature_rule["id"],
         reference_column = "feature_id"
      )

   for table in feature_tables:
      table_name = st.text_input(
         label = lockey("rule_label_table_name"),
         placeholder = table["table_name"]
      )

      query_select = st.text_area(
         label = lockey("rule_label_query_select")
      )

      query_execute = st.text_area(
         label = lockey("rule_label_query_execute") 
      )


   st.divider()