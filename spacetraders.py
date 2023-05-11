import requests
import json

# divide classes into systems
# agent, nav, ship, contracts, etc.
# trader inherits systems
class Agent:
    URL = 'https://api.spacetraders.io'

    def getToken(self, token):
        with open(token) as f:
            data = json.loads(f.read())
        return data['token']
    
    def getAgent(self, authHeaders):
        agentURL = f"{self.URL}/v2/my/agent"
        print(agentURL)
        r = requests.get(url=agentURL, headers=authHeaders)
        agentData = r.json()

        return agentData

class Navigation(Agent):

    def getLocation(self, data=False):
        headquarters = self.agent['data']['headquarters'].split('-')

        location = {
            'sector': headquarters[0],
            'system': '-'.join(headquarters[0:2]),
            'waypoint': '-'.join(headquarters[0:3])
        }

        locationURL = f"{self.URL}/v2/systems/{location['system']}/waypoints/{location['waypoint']}"
        print(locationURL)

        r = requests.get(url = locationURL, headers = self.authHeaders)
        # print(r)
        locationData = r.json()
        if data:
            return (location, locationData)
        else:
            return location

    def getWaypoints(self, waypointType=None):
        waypointURL = f"{self.URL}/v2/systems/{self.location['system']}/waypoints"
        r = requests.get(url = waypointURL, headers = self.authHeaders)
        waypointData = r.json()

        if waypointType:
            for waypoint in waypointData['data']:
                print(waypoint['type'])
                if waypoint['type'] == waypointType:
                    return waypoint
        
        return waypointData

    def getShipyardInventory(self, location):
        shipyardWaypoint = self.getWaypoints(waypointType='ORBITAL_STATION')
        shipyardURL = f'{self.URL}/v2/systems/{location}/waypoints/{shipyardWaypoint}'

        r = requests.get(url = shipyardURL, headers = self.authHeaders)
        return r.json()

class Contract(Agent):

    def getContracts(self):
        contractsURL = f"{self.URL}/v2/my/contracts"
        r = requests.get(url = contractsURL, headers = self.authHeaders)
        contractsData = r.json()
        accepted = contractsData['data'][0]['accepted']

        for contract in contractsData['data']:
            self.printContract(contract)

        if not accepted:
            accept = input('Accept contract {id}? (y/n): '.format(id=contractsData['data'][0]['id'].upper()))
            if accept == 'y':
                r = requests.post(url = contractsURL + '/{id}/accept'.format(id = contractsData['data'][0]['id']), headers=self.authHeaders)
                print(r.json())
    
    def printContract(self, contract):
        contractString = 'Contract ID: {id}\nOffered By: {faction}\nContract Type: {type}\n' \
                        'Deliver {unitsRequired} units of {commodity} to {destination} by {deadline}\n'\
                        'Payment:\n\tAdvance:\t{onAccepted}c\n\tOn Completion:\t{onFulfilled}c\nExpiration: {expiration}'
        terms = contract['terms']
        deliver = terms['deliver']
        
        print(contractString.format(
                id = contract['id'].upper(),
                faction = contract['factionSymbol'],
                type = contract['type'],
                unitsRequired = deliver[0]['unitsRequired'],
                commodity = deliver[0]['tradeSymbol'],
                destination = deliver[0]['destinationSymbol'],
                deadline = terms['deadline'],
                onAccepted = terms['payment']['onAccepted'],
                onFulfilled = terms['payment']['onFulfilled'],
                expiration = contract['expiration']
            )
        )

class Trader(Navigation, Contract):

    def __init__(self, token):
        self.token = self.getToken(token)
        self.authHeaders = {"Authorization": f"Bearer {self.token}"}
        self.agent = self.getAgent(self.authHeaders)
        self.location, self.locationData = self.getLocation(data=True)
        


trader = Trader('./token/token.json')
print(trader.getShipyardInventory(trader.location['system']))
# print(trader.getContracts())