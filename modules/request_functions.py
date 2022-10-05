import requests

def check_url(url):
    userdata = {"check": "1"}
    resp = requests.post(url,
                         json=userdata,
                         headers={"Content-Type": "application/json"}, )
    return True if resp.status_code == 200 else False

def get_response(url, userdata, resp_type='string'):
    resp = requests.post(url,
                         json=userdata,
                         headers={"Content-Type": "application/json"}, )
    if resp.status_code == 200:
        if resp_type == 'json':
            return resp.json()
        elif resp_type == 'string':
            return resp.text