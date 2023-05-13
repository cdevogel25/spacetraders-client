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

        return r.json()['data']

class Navigation:
    
    def __init__(self, baseURL, system, auth):
        self.navURL = f'{baseURL}/v2/systems'
        self.waypoints = self.getWaypoints(system, auth)

    def getWaypoints(self, system, auth):
        waypointURL = f'{self.navURL}/{system}/waypoints'
        r = requests.get(url = waypointURL, headers = auth)

        return r.json()['data']
    
    # TODO: system map/nearby system map functions
    def systemMap(self, system, auth):
        pass
    
class Ship(Navigation):

    def __init__(self, baseURL, shipName, auth):
        self.shipURL = f'{baseURL}/v2/my/ships/{shipName}'
        self.shipInfo = self.getShipInfo(auth)
        self.nav = Navigation(baseURL, self.shipInfo['nav']['systemSymbol'], auth)

    def debug(self):
        pass

    def getShipInfo(self, auth):
        r = requests.get(url = self.shipURL, headers = auth)

        return r.json()['data']
    
    # Basic movement orders
    def dockDepart(self, auth):
        if self.shipInfo['nav']['status'] == 'DOCKED':
            confirmDeparture = input('Confirm Departure? (y/n): ')
            if confirmDeparture == 'y':
                dockDepartURL = f'{self.shipURL}/orbit'
            else:
                return
        elif self.shipInfo['nav']['status'] == 'ORBIT': #this might not be what it is
            confirmDock = input('Confirm Docking? (y/n): ')
            if confirmDock == 'y':
                dockDepartURL = f'{self.shipURL}/dock'
            else:
                return
        
        r = requests.post(url = dockDepartURL, headers = auth)

        return r.json()['data']
    
    def shipFlightMode(self, header, mode):
        r = requests.patch(url = f'{self.shipURL}/nav', headers = header, json = {'flightMode': mode})

        return r.json()['data']

    def shipWaypointNavigate(self, header, waypoint):
        r = requests.post(f'{self.shipURL}/navigate', headers = header, json = {'waypointSymbol': waypoint})

        return r.json()['data']
    
    # Interstellar movement orders
    def shipWarp(self, header, destination):
        r = requests.post(f'{self.shipURL}/warp', headers = header, json = {'systemSymbol': destination})

        return r.json()['data']
    
    def shipJump(self, header, destination):
        r = requests.post(f'{self.shipURL}/jump', headers = header, json = {'systemSymbol': destination})

        return r.json()['data']

class Contract:

    def __init__(self, baseURL, auth):
        self.contractsURL = f'{baseURL}/v2/my/contracts'
        self.contracts = self.getContracts(auth)

    def getContracts(self, auth):
        r = requests.get(url = self.contractsURL, headers = auth)

        return r.json()['data']
    
    # do you need this??
    def getContract(self, contractID, auth):
        r = requests.get(url = f'{self.contractsURL}/{contractID}', headers = auth)

        return r.json()['data']
    
    def acceptContract(self, contractID, auth):
        r = requests.get(url = f'{self.contractsURL}/{contractID}/accept', headers = auth)

        return r.json()['data']

class Trader(Agent):

    def __init__(self, token, shipList=[]):
        self.token = self.getToken(token)
        self.authHeaders = {'Authorization': f'Bearer {self.token}'}
        self.agent = self.getAgent(self.authHeaders)
        self.ships = [Ship(self.URL, ship, self.authHeaders) for ship in shipList]
        self.contract = Contract(self.URL, self.authHeaders)
    
    def purchaseShip(self, shipType, shipyardWaypoint):
        r = requests.post(
            url = f'{self.URL}/v2/my/ships',
            header = {**self.autHeaders, **self.contentHeader},
            json = {'shipType': shipType, 'waypointSymbol': shipyardWaypoint}
        )

        return r.json()['data']

    def getHeadquarters(self, data=False):
        headquarters = self.agent['headquarters'].split('-')

        location = {
            'sector': headquarters[0],
            'system': '-'.join(headquarters[0:2]),
            'waypoint': '-'.join(headquarters[0:3])
        }

        r = requests.get(
            url = f"{self.URL}/{location['system']}/waypoints/{location['waypoint']}",
            headers = self.authHeaders
        )

        locationData = r.json()['data']
        if data:
            return (location, locationData)
        else:
            return location