import requests
import time
from fake_useragent import UserAgent

def do_request(url, attempt=3, userdata=None):
    resp = None
    ua = UserAgent()
    user_agent = ua.random
    headers = {'user-agent': user_agent}
    try:
        if userdata is None:
            resp = requests.get(url, headers=headers,)
        else:
            resp = requests.post(url, json=userdata, headers=headers,)
    except requests.RequestException:
        if attempt:
            time.sleep(5)
            return do_request(url, attempt - 1, userdata)
    finally:
        return resp