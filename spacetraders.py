import requests
import json

URL = 'https://api.spacetraders.io/v2/my/agent'
# headers = {"Authorization": "Bearer {token}"}

def getToken():
    with open('token.json') as f:
        data = json.loads(f.read())
    return data['token']

token = getToken()
headers = {"Authorization": "Bearer {}".format(token)}

r = requests.get(url=URL, headers=headers)
print(r.text)