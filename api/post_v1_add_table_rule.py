from common_handling import set_lockey
from common_handling import set_client
from common_handling import response

lockey = set_lockey.execute

def execute(request):
    client = set_client.execute()

    # try:
    #     table_rule = client.table("tables").select("id").eq(request["name"]).execute().data

    client.table("tables").insert(request).execute()