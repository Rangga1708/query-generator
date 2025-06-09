import pandas as pd
import json
from common_handling import response

def execute():
    try:
        config = json.loads(open("config.json"))
    except Exception as e:
        config = json.load(open("config.json"))
    
    return response.execute("SUCCESS", 
                            "Config key fetched successfully",
                            config)