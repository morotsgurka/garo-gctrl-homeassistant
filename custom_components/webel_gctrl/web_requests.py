import requests
import json
import re
from datetime import datetime, timedelta

login_url_mobile= 'http://webel-online.se/mobile/login.asp'
secure_url_mobile= 'http://webel-online.se/mobile/mobile.asp'
mobile_request_url = 'http://webel-online.se/mobile/ajax/mobileajax.asp'
energy_url = 'http://webel-online.se/mobile/mobile.asp'

login_payload = {
    'lang': 'se',
    'username': '',
    'password': ''
}

OUTLET_ID_PATTERN = re.compile(r"id:\s*'([0-9A-Z\-]+)'")
DIRECTSTART_TEXT_PATTERN = re.compile(r"Aktiverat till\s*([0-9]{2}:[0-9]{2})")

def check_credentials():
    """Ensure credentials are present in login_payload.

    In Home Assistant we never prompt; credentials must be provided
    via configuration. If they are missing, just raise an error.
    """
    if login_payload["username"] == "" or login_payload["password"] == "":
        raise RuntimeError("Webel credentials not set in login_payload")

def get_dynamic_id(session: requests.Session) -> str:
    """
    Fetch mobile.asp and extract the outlet ID dynamically.
    """
    resp = session.get(secure_url_mobile)
    resp.raise_for_status()
    m = OUTLET_ID_PATTERN.search(resp.text)
    if not m:
        raise RuntimeError("Could not find outlet ID in mobile.asp")
    #print(f"Found dynamic outlet ID: {m.group(1)}")
    return m.group(1)


def fetch_all_bookings():
    """
    Log in, get dynamic outlet id, and fetch all bookings.
    Returns a dict with raw strings and parsed lists.
    """
    check_credentials()
    with requests.session() as s:
        # login
        s.post(login_url_mobile, data=login_payload)
        outlet_id = get_dynamic_id(s)

        payload = {
            'action': 'fetchallbookings',
            'id': outlet_id,
        }
        r = s.post(mobile_request_url, data=payload)
        data = r.json()

        if int(data.get('success', "0")) < 1:
            print("Failed to fetch bookings")
            print(json.dumps(data, indent=4, sort_keys=True))
            return None

        # Raw strings from server
        periodbookings_raw = data.get('periodbookings', '') or ''
        bookings_raw = data.get('departurebookings', '') or ''
        the_function = int(data.get('thefunction', 0))

        # Split into lists, dropping empty trailing entries
        period_list = [p for p in periodbookings_raw.split('|') if p]
        booking_list = [b for b in bookings_raw.split('|') if b]

        return {
            "raw": data,
            "the_function": the_function,
            "period_strings": period_list,
            "booking_strings": booking_list,
        }

def turn_on(minutes: int = 120):
    check_credentials()
    with requests.session() as s:
        # login
        s.post(login_url_mobile, data=login_payload)
        outlet_id = get_dynamic_id(s)
        # runtime -1 == 24h
        start_payload = {
            'action': 'directstart',
            'id': outlet_id,
            'runtime': str(minutes),
        }
        result = perform_action_with_session(s, start_payload)
        return result[0]


def turn_off():
    check_credentials()
    with requests.session() as s:
        s.post(login_url_mobile, data=login_payload)
        outlet_id = get_dynamic_id(s)

        stop_payload = {
            'action': 'canceldirectstart',
            'id': outlet_id,
        }
        result = perform_action_with_session(s, stop_payload)
        return result[0]

def check_state():
    """
    Log in, load mobile.asp, and determine if the outlet is ON or OFF
    by inspecting the 'cancel_directstart' button text.
    Returns a dict: {"on": bool, "until": "HH:MM" or None}
    """
    check_credentials()
    with requests.session() as s:
        # login
        s.post(login_url_mobile, data=login_payload)

        # load mobile.asp (this is where the button HTML is)
        resp = s.get(secure_url_mobile)
        resp.raise_for_status()
        html = resp.text

        # Look for the cancel_directstart button and its text
        # The server-side HTML has: <button class="cancel_directstart" ...>Avbryt direktstart</button>
        # But JS later changes it to: "Aktiverat till 16:30  -  Avbryt direktstart"
        # So we just search for that phrase and extract the time.
        m = DIRECTSTART_TEXT_PATTERN.search(html)
        if m:
            until_time = m.group(1)  # e.g. "16:30"
            return {"on": True, "until": until_time}
        else:
            # No "Aktiverat till ..." text present → treat as OFF
            return {"on": False, "until": None}

def perform_action_with_session(s: requests.Session, payload: dict):
    """
    Perform an action using an existing logged-in session.
    Assumes 'id' is already present in payload.
    """
    # Ensure we have loaded mobile.asp at least once (sets cookies etc.)
    s.get(secure_url_mobile)

    action = s.post(mobile_request_url, data=payload)
    json_response = action.json()
    if int(json_response.get('success', "0")) == 1:
        if payload['action'] == 'directstart':
            return True, json_response.get('directstartuntil')
        else:
            return True, None
    else:
        return False, None
    

def sort_energy_json(json_response):
    timestamps = json_response['timestamps'].split('|')
    values = json_response['values'].split('|')
    sorted_json = dict(zip(timestamps, values))
    return sorted_json


def get_energyusage_raw(from_date: str | None = None, to_date: str | None = None):
    """Return raw JSON from fetchenergy for a given date range.

    If from_date/to_date are None, default to the current month.
    """
    check_credentials()
    with requests.session() as s:
        s.post(login_url_mobile, data=login_payload)
        outlet_id = get_dynamic_id(s)

        if from_date is None or to_date is None:
            today = datetime.utcnow().date()
            first = today.replace(day=1)
            # Next month first day, then back one day
            if first.month == 12:
                next_month_first = first.replace(year=first.year + 1, month=1)
            else:
                next_month_first = first.replace(month=first.month + 1)
            last = next_month_first - timedelta(days=1)
            from_date = first.isoformat()
            to_date = last.isoformat()

        energy_payload = {
            'action': 'fetchenergy',
            'id': outlet_id,
            'fromDate': from_date,
            'toDate': to_date,
            'resolution': 'DAY'
        }
        energy = s.post(mobile_request_url, data=energy_payload)
        return energy.json()


def get_energyusage():
    """Convenience wrapper for manual testing: print sorted energy JSON."""
    json_response = get_energyusage_raw()
    if json_response.get('success') == '1':
        print(sort_energy_json(json_response))
    else:
        print("Failed to get energy usage")


## Test stuff below here

if __name__ == "__main__":
    # Simple manual test runner; will only execute when called directly.

    # set login credentials here for testing using input()
    login_payload["username"] = input("Enter Webel username: ")
    login_payload["password"] = input("Enter Webel password: ")
    #print(check_state())
    #print(fetch_all_bookings())
    print(get_energyusage())
