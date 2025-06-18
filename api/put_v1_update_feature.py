from common_handling import set_lockey
from common_handling import set_client
from common_handling import response

lockey = set_lockey.execute

def execute(request):
    if not is_request_feature_valid(request["feature"]):
        return response.execute(
            status = "30001",
            message = lockey("rule_label_invalid_input"),
            data = {}
        )
    
    if not is_request_table_valid(request["tables"]):
        return response.execute(
            status = "30001",
            message = lockey("rule_label_invalid_input"),
            data = {}
        ) 

    client = set_client.execute()

    try:
        client.table("features").update(request["feature"]).eq("id", request["feature"]["id"]).execute()
    except:
        return response.execute(
            status = "80000",
            message = lockey("rule_label_update_failed"),
            data = {}
        )
    
    for table in request["tables"]:
        try:
            client.table("tables").update(table).eq("id", table["id"]).execute()
        except:
            return response.execute(
                status = "80000",
                message = lockey("rule_label_update_failed"),
                data = {}
            )
    
    return response.execute(
        status = "200",
        message = lockey("rule_label_update_success"),
        data = {}
    )

def is_request_feature_valid(request):
    return request["name"] != ''

def is_request_table_valid(request):
    for table in request:
        if ((table["table_name"] is None) or
            (table["query_select"] is None) or
            (table["query_execute"] is None)):
            return False
        
        for column in table["columns"]:
            if (column["name"] is None) or (column["name"] == ""):
                return False

    return True