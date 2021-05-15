import json

data = {"id": "123123", "score": 30}

json_data = json.dumps(data)
print(bytes(json_data, 'utf-8'))