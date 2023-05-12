import requests
import json

# divide systems into classes
# agent, nav, ship, contracts, etc.
# trader inherits systems
class Agent:
    URL = 'https://api.spacetraders.io'
    contentHeader = {'Content-Type': 'application/json'}

    def getToken(self, token):
        with open(token) as f:
            data = json.loads(f.read())

        return data['token']
    
    def getAgent(self, authHeaders):
        r = requests.get(url=f'{self.URL}/v2/my/agent', headers=authHeaders)
        agentData = r.json()

        return agentData
    
class Ship(Agent):
    
    SHIP_URL = f'{Agent.URL}/v2/my/ships'

    def __init__(self, shipName):
        self.shipInfo = self.getShipInfo(shipName)
        print(self.shipInfo)

    def getShipInfo(self, shipName):
        shipURL = f'{self.SHIP_URL}/{shipName}'
        r = requests.get(url = shipURL, headers = self.authHeaders)
        return r.json()
    
    def shipWaypointNavigate(self, shipName, waypoint):
        navigateURL = f'{self.SHIP_URL}/{shipName}/navigate'
        r = requests.post(url = navigateURL, headers = {**self.authHeaders, **self.contentHeader}, json = {'waypointSymbol': waypoint})

        return r.json()
    
    def shipOrbit(self, shipName):
        orbitURL = f'{self.SHIP_URL}/{shipName}/orbit'
        r = requests.post(url = orbitURL, headers = self.authHeaders)

        return r.json()
    
    def shipDock(self, shipName):
        dockURL = f'{self.SHIP_URL}/{shipName}/dock'
        r = requests.post(url = dockURL, headers = self.authHeaders)

        return r.json()
    
    def shipFlightMode(self, shipName, mode):
        flightModeURL = f'{self.SHIP_URL}/{shipName}/nav'
        r = requests.patch(url = flightModeURL, headers = {**self.authHeaders, **self.contentHeader}, json = {'flightMode': mode})

        return r.json()
    
    def shipWarp(self, shipName, destination):
        warpURL = f'{self.SHIP_URL}/{shipName}/warp'
        r = requests.post(url = warpURL, headers = {**self.authHeaders, **self.contentHeader}, json = {'systemSymbol': destination})

        return r.json()
    
    def shipJump(self, shipName, destination):
        jumpURL = f'{self.SHIP_URL}/{shipName}/jump'
        r = requests.post(url = jumpURL, headers = {**self.authHeaders, **self.contentHeader}, json = {'systemSymbol': destination})

        return r.json()

class Navigation(Ship):

    NAV_URL = f'{Agent.URL}/v2/systems'

    def getHeadquarters(self, data=False):
        headquarters = self.agent['data']['headquarters'].split('-')

        location = {
            'sector': headquarters[0],
            'system': '-'.join(headquarters[0:2]),
            'waypoint': '-'.join(headquarters[0:3])
        }

        locationURL = f"{self.NAV_URL}/{location['system']}/waypoints/{location['waypoint']}"

        r = requests.get(url = locationURL, headers = self.authHeaders)

        locationData = r.json()
        if data:
            return (location, locationData)
        else:
            return location

    def getWaypoints(self, waypointType=None):
        waypointURL = f"{self.NAV_URL}/{self.location['system']}/waypoints"
        r = requests.get(url = waypointURL, headers = self.authHeaders)
        waypointData = r.json()

        if waypointType:
            for waypoint in waypointData['data']:
                if waypoint['type'] == waypointType:
                    return waypoint
                  
        return waypointData

    def getShipyardInventory(self, location):
        shipyardWaypoint = self.getWaypoints(waypointType='ORBITAL_STATION')['symbol']
        shipyardURL = f'{self.NAV_URL}/{location}/waypoints/{shipyardWaypoint}/shipyard'

        r = requests.get(url = shipyardURL, headers = self.authHeaders)

        with open('./data/shipyardData.json', 'w') as f:
            f.write(json.dumps(r.json(), indent=4))

class Contract(Agent):

    CONTRACTS_URL = f'{Agent.URL}/v2/my/contracts'

    def getContracts(self):
        r = requests.get(url = self.CONTRACTS_URL, headers = self.authHeaders)
        
        return r.json()
    
    def getContract(self, contractID):
        r = requests.get(url = f'{self.CONTRACTS_URL}/{contractID}', headers = self.authHeaders)

        return r.json()
    
    def acceptContract(self, contractID):
        r = requests.post(url = f'{self.CONTRACTS_URL}/{contractID}/accept', headers = self.authHeaders)

        return r.json()

class Trader(Navigation, Contract):

    def __init__(self, token, shipList):
        self.token = self.getToken(token)
        self.authHeaders = {"Authorization": f"Bearer {self.token}"}
        self.agent = self.getAgent(self.authHeaders)
        for ship in shipList:
            self.ships.append(self.getShipInfo(ship))

    def purchaseShip(self, shipType, shipyardWaypoint):
        purchaseURL = f'{self.URL}/v2/my/ships'
        r = requests.post(url = purchaseURL, headers = {**self.authHeaders, **self.contentHeader}, json = {'shipType': shipType, 'waypointSymbol': shipyardWaypoint})

        return r.json()
        


trader = Trader('./token/token.json', ['VITAMINC-1'])