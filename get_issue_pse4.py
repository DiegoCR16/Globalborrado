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

# Try to get issue PSE-4 directly or search for it
url = 'https://equipo05-globalexchange.atlassian.net/rest/api/3/issue/PSE-4'
res = requests.get(url, headers=headers)
print('Issue PSE-4:', res.status_code, res.text)

if res.status_code != 200:
    # Try search
    search_url = 'https://equipo05-globalexchange.atlassian.net/rest/api/3/search?jql=key=PSE-4'
    res_search = requests.get(search_url, headers=headers)
    print('Search PSE-4:', res_search.status_code, res_search.text)
