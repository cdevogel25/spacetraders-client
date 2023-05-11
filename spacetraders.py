import requests
import json

class sTrader:

    URL = 'https://api.spacetraders.io/{}'

    def __init__(self, token):
        self.token = self.getToken(token)
        self.authHeaders = {"Authorization": "Bearer {}".format(self.token)}
        self.agent = self.getAgent()

    def getToken(self, token):
        with open(token) as f:
            data = json.loads(f.read())
        return data['token']
    
    def getAgent(self):
        agentURL = self.URL.format('v2/my/agent')
        r = requests.get(url=agentURL, headers=self.authHeaders)
        agentData = r.json()

        return agentData

    def getLocation(self):
        headquarters = self.agent['data']['headquarters'].split('-')

        location = {
            'sector': headquarters[0],
            'system': '-'.join(headquarters[0:2]),
            'waypoint': '-'.join(headquarters[0:3])
        }

        locationURL = 'v2/systems/{systemSymbol}/waypoints/{waypointSymbol}'.format(
            systemSymbol=location['system'],
            waypointSymbol=location['waypoint']
        )

        r = requests.get(url=self.URL.format(locationURL), headers=self.authHeaders)
        locationData = r.json()
        return locationData

trader = sTrader('./token/token.json')

print(trader.getLocation())