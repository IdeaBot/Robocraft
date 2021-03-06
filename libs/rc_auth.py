import requests

# NOTE: This is a burner account, with no items unlocked
USERNAME = 'FJAPIC00L'
EMAIL = 'melon.spoik@gmail.com'
PASSWORD = 'P4$$w0rd'

def fj_login(name=USERNAME, password=PASSWORD, email_mode=False, _print=False):
    if email_mode:
        url = 'https://account.freejamgames.com/api/authenticate/email/web'
        body_json = {'EmailAddress':name, 'Password':password}
        response = requests.post(url, json=body_json)
    else:
        url = 'https://account.freejamgames.com/api/authenticate/displayname/web'
        body_json = {'DisplayName':name, 'Password':password}
        response = requests.post(url, json=body_json)
    if response.status_code != 200:
        if _print:
            print('FJ Auth returned error', response.status_code)
    return response.json()

def make_headers(token):
    headers = dict()
    headers['Authorization'] = "Web "+token
    return headers
