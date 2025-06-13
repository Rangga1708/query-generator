from common_handling import set_client

def execute(request):
    client = set_client.execute()
    client.table("features").update(request["feature"]).eq("id", request["feature"]["id"]).execute()
    
    for table in request["tables"]:
        client.table("tables").update(table).eq("id", table["id"]).execute()