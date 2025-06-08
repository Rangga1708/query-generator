import pandas as pd
import json
from common_handling import response

def execute():
    localization_key = json.load(open("lockey.json"))
    
    return response.execute("SUCCESS", 
                            "Localization key fetched successfully",
                            localization_key)