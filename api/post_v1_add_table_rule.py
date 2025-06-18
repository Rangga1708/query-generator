import json
from common_handling import set_lockey
from common_handling import set_client
from common_handling import response

lockey = set_lockey.execute

def execute(request):
    try:
        request["columns"] = json.loads(request["columns"])
    except:
        return response.execute(
            status = "30001",
            message = lockey("rule_label_invalid_input"),
            data = {}
        ) 

    if not is_request_valid(request):
        return response.execute(
            status = "30001",
            message = lockey("rule_label_invalid_input"),
            data = {}
        ) 

    client = set_client.execute()

    try:
        table_rule = (
            client
            .table("tables")
            .select("id")
            .eq("table_name", request["table_name"])
            .eq("query_select", request["query_select"])
            .eq("query_execute", request["query_execute"])
            .eq("columns", request["columns"])
            .execute()
            .data)
        
        if len(table_rule) != 0:
            return response.execute(
                status = "30003",
                message = lockey("rule_label_table_rule_already_exist"),
                data = {}
            )
        
    except:
        return response.execute(
            status = "80000",
            message = lockey("rule_label_add_new_table_rule_failed"),
            data = {}
        )
    
    try:
        client.table("tables").insert(request).execute()
        
        return response.execute(
                status = "200",
                message = lockey("rule_label_add_new_table_rule_success"),
                data = {}
            )
    
    except:
        return response.execute(
            status = "80000",
            message = lockey("rule_label_add_new_table_rule_failed"),
            data = {}
        )

def is_request_valid(request):
    if ((request["table_name"] == '') or
        (request["query_select"] == '') or
        (request["query_execute"] == '') or
        (request["columns"] == [])):
        return False
    
    for column in request["columns"]:
        if (("name" not in column) or
            ("lov" not in column)):
            return False
        elif column["name"] == "":
            return False
        elif type(column["lov"]) != type([]):
            return False

    return True