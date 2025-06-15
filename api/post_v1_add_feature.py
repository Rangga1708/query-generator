from common_handling import set_client

def execute(request):
    client = set_client.execute()
    client.table("features").insert(request).execute()