import json
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
        try:
            table["columns"] = json.loads(table["columns"])
        except:
            print(1)
            return False

        if ((table["table_name"] == '') or
            (table["query_select"] == '') or
            (table["query_execute"] == '') or
            (table["columns"] == [])):
            print(2)
            return False
        
        for column in table["columns"]:
            if (("name" not in column) or
                ("lov" not in column)):
                print(3)
                return False
            elif column["name"] == "":
                print(4)
                return False
            elif type(column["lov"]) != type([]):
                print(5)
                return False

    return True