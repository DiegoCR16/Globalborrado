import requests
import json
import base64

email = 'diegocan1804@gmail.com'
token = 'ATATT3xFfGF0STyUFWbjVGPQhPFZcsHg7_48vQHClSJTyRyEoCfLw4cMdoVJbGwflemOFtIoATF0q9dcuNHT5WqwojGW2J0h16UgQV94rRsmxBx54DND3jcjvYePN0PI4aQYp6FN8SylxBduDI8h7kJHh1rT3SS4gg8qf0YVE-yYYKhjrelEp-M=7A21EC28'
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
