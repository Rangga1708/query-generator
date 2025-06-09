import streamlit as st
import pandas as pd
from common_handling import set_lockey, find_config, find_value_in_dataframe

lockey = set_lockey.execute
config = find_config.execute

def app():
    features = pd.DataFrame(config("features"))
    tables = pd.DataFrame(config("tables"))

    tabs = st.tabs([
        lockey("rule_title_insert_feature"),
        lockey("rule_title_insert_table")
    ])

    with tabs[0]:
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