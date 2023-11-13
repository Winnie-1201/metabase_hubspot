from spin_http import Response, Request, http_send
from spin_config import config_get
import json
from datetime import datetime

def handle_request(request):
    query_list = [1519, 1605, 1608, 1609, 1611, 1669, 1670, 1671]
    payload = {"username":config_get("username"), "password":config_get("password")}
   
    encoded = json.dumps(payload, indent=2).encode('utf-8')
    token = http_send(
        Request("POST",
                f"https://fermyon.metabaseapp.com/api/session",
                {"Content-Type": "application/json"},
                body=encoded
                )
    )

    token_json = token.body.decode('utf-8')
    parsed_token = json.loads(token_json)
    responses = []
    try:
    # Fetch the data from Metabase
        for q in query_list:
            response = http_send(
                Request("POST",
                        f"https://fermyon.metabaseapp.com/api/card/{q}/query",
                        {"X-Metabase-Session": parsed_token['id']},
                        None
                        )
            )
            res_json = response.body.decode('utf-8')
            data = json.loads(res_json)
            metabase = data['data']['rows']
            column = data['data']['cols'][1]['display_name']
            responses.append({column: metabase})
            

        # data from Metabase is a list of array
        # each subarray has two elements [contact_id, values]
        token = config_get("token")
        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': f"Bearer {token}"
        }

        for item in responses:
            key = next(iter(item.keys()))
            value = item[key]

            properties = {"inputs": []}

            for idx, s in enumerate(value):
                data = int(datetime.fromisoformat(s[1].split("T")[0]).timestamp()*1000) if key == 'date_of_most_recent_usage' else s[1]
                contact_id = s[0]
                properties["inputs"].append({"id":str(contact_id), 
                                    "properties": {key:data}
                                    })
                if len(properties["inputs"]) == 100 or idx == len(value) - 1:
                    encode_payload = json.dumps(properties, indent=2).encode('utf-8')
                    host = config_get("hubspot_host")
                    uri = f"{host}/crm/v3/objects/contacts/batch/update"

                    response = http_send(
                        Request("POST", uri, body=encode_payload, headers=headers)
                    )

                    properties["inputs"] = []


    except Exception as e:
        return Response(500,
                    {"content-type": "text/plain"},
                    bytes(f"{e}", "utf-8"))

    return Response(200,
                    {"content-type": "text/plain"},
                    bytes(f"Sucessfully updated!", "utf-8"))
