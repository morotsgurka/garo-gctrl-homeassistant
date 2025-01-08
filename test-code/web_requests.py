import requests
import json

login_url_mobile= 'http://webel-online.se/mobile/login.asp'
secure_url_mobile= 'http://webel-online.se/mobile/mobile.asp'
mobile_request_url = 'http://webel-online.se/mobile/ajax/mobileajax.asp'
energy_url = 'http://webel-online.se/mobile/mobile.asp'
#{"success": "1"}

#    "action": "directstart",
#    "directstartuntil": "22:41",
#    "success": "1"
#}
login_payload = {
    'lang': 'se',
    'username': 'your-username',
    'password': 'your-password'
}

def turn_on():
    start_payload = {
        'action': 'directstart',
        'id': '000-000-017-173-A0',
        'runtime': '120'
    }
    result = perform_action(start_payload)
    if result[0]:
        return True
        #print("Turned on outlet until "+result[1]+"")
    else:
        return False
        #print("Failed to turn on outlet")


def turn_off():
    stop_payload = {
        'action': 'canceldirectstart',
        'id': '000-000-017-173-A0',
    }
    result = perform_action(stop_payload)
    if result[0]:
        return True
        #print("Turned off outlet")
    else:
        return False
        #print("Failed to turn off outlet")


def perform_action(payload):
    with requests.session() as s:
        s.post(login_url_mobile, data=login_payload)
        r= s.get(secure_url_mobile)
        action = s.post(mobile_request_url, data=payload)
        json_response = action.json()
        if json_response['success'] == '1':
            #print(json.dumps(json_response, indent=4, sort_keys=True))
            if payload['action'] == 'directstart':
                return True, json_response['directstartuntil']
            else:
                return True, None
        else:
            #print("Failed to perform action: "+payload['action'])
            return False, None
    
def sort_energy_json(json_response):
    timestamps = json_response['timestamps'].split('|')
    values = json_response['values'].split('|')
    sorted_json = dict(zip(timestamps, values))
    return sorted_json


def get_energyusage():
    energy_payload = {
        'action': 'fetchenergy',
        'id': '000-000-017-173-A0',
        'fromDate': '2023-11-01',
        'toDate': '2023-11-30',
        'resolution': 'DAY'
    }
    with requests.session() as s:
        s.post(login_url_mobile, data=login_payload)
        energy = s.post(mobile_request_url, data=energy_payload)
        json_response = energy.json()
        if json_response['success'] == '1':
            print(sort_energy_json(json_response))
        else:
            print("Failed to get energy usage")


## Test stuff below here

#get_energyusage()
#turn_on()
#turn_off()
