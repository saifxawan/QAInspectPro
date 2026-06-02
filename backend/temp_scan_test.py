import requests
from seed_user import seed_user
seed_user()
print('User seeded')
resp = requests.post('http://127.0.0.1:8000/api/auth/login', data={'username':'admin','password':'admin123'})
print('Login', resp.status_code, resp.text)
if resp.status_code == 200:
    token = resp.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    target = 'https://example.com'
    scan_resp = requests.post('http://127.0.0.1:8000/api/scan/', json={'url': target}, headers=headers)
    print('Scan', scan_resp.status_code, scan_resp.text)
    get_resp = requests.get('http://127.0.0.1:8000/api/scan/results/' + requests.utils.quote(target, safe=''), headers=headers)
    print('Results', get_resp.status_code, get_resp.text)
else:
    print('Login failed, cannot test scan')
