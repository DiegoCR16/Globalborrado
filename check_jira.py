import requests
import json
import base64

email = 'diegocan1804@gmail.com'
token = 'ATATT3xFfGF0aUOWxABPU673WAVc7xiliCK_w-drXktItV3hZEcmHz_IS3LNPwgnXnWBIpVWwiVyzEgSjhb04UwbUMxr5li73Tl_fI0-c8buwJCchusbyW53FE3U93onRgSd_yaloAftlWt9jfrKV7p6fZHg3SrmX16jzUEzkCqXD8-8xhimBgY=6AA6D6B1'
credentials = f"{email}:{token}"
encoded = base64.b64encode(credentials.encode()).decode()

headers = {
    'Accept': 'application/json',
    'Authorization': f'Basic {encoded}'
}

res = requests.get('https://equipo05-globalexchange.atlassian.net/rest/api/3/myself', headers=headers)
print('Myself:', res.status_code, res.text)

res2 = requests.get('https://equipo05-globalexchange.atlassian.net/rest/api/3/project', headers=headers)
print('Projects:', res2.status_code, res2.text)
