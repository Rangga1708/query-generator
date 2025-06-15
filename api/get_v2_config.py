import pandas as pd
import json
from common_handling import response, set_client

client = set_client.execute()

def execute():
    features = (
        client
        .table("features")
        .select("id, name, notes")
        .order("name")
        .execute()
        .data
        )
    
    tables = (
        client
        .table("tables")
        .select("id, feature_id, table_name, query_select, query_execute, columns")
        .execute()
        .data
        )

    data = {
        "features": features,
        "tables": tables
    }

    return response.execute("SUCCESS", 
                            "Config key fetched successfully",
                            data)