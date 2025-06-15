from common_handling import set_lockey
from common_handling import set_client
from common_handling import response

lockey = set_lockey.execute

def execute(request):
    client = set_client.execute()

    try:
        feature_data = (
            client
            .table("features")
            .select("name")
            .eq("name", request["name"])
            .execute()
            .data
        )

        if len(feature_data) != 0:
            return response.execute(
                status = "30001",
                message = lockey("rule_label_feature_already_exist"),
                data = {}
            )
        
    except:
        return response.execute(
            status = "80000",
            message = lockey("rule_label_add_new_feature_failed"),
            data = {}
        )

    try:
        client.table("features").insert(request).execute()

        return response.execute(
                status = "200",
                message = lockey("rule_label_add_new_feature_success"),
                data = {}
            )
    
    except:
        return response.execute(
            status = "80000",
            message = lockey("rule_label_add_new_feature_failed"),
            data = {}
        )