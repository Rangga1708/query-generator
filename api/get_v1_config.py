import pandas as pd
import json
from common_handling import response

def execute():
    config = json.load(open("config.json"))
    
    return response.execute("SUCCESS", 
                            "Config key fetched successfully",
                            config)