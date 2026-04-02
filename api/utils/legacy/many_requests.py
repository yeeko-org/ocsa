
def send_many_requests():
    import requests
    import json
    import time

    error_ids = [2107]
    # 2075
    all_ids = [
        2107, 2005, 1902, 1896, 1833, 1832, 1737, 1571, 1501,
        1450, 1405, 1270, 797, 760, 718, 49]
    url = "https://ocsa.ibero.mx/api/rpc/approve_draft"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoib2Nzd2ViYWRtaW4iLCJlbWFpbCI6InNlYmFzdGlhbi5vbHZlcmFAaWJlcm8ubXgifQ.boDDaOPQXa9Q3LMohHXQvuw85fR5rEKPcMxr4nqzGms'
    }

    for elem_id in all_ids:
        payload = {'_id': elem_id}
        with requests.Session() as session:
            response = session.post(
                url, headers=headers, data=json.dumps(payload))
            if response.text:
                print(f"elem_id: {elem_id} | response: {response.text}")
        time.sleep(35)


def model_fields():
    from django.apps import apps
    my_model = apps.get_model("source", "Note")
    fields = my_model._meta.get_fields()
    for field in fields:
        try:
            print(field.default)
            print(type(field.default))
        except AttributeError:
            pass

