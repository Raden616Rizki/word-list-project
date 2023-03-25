import requests

api_key = 'a04c28b0-6c7b-468f-967d-b3e54dab8cca'
word = 'potato'
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

res = requests.get(url)

definitions = res.json()

for definition in definitions:
    print(definition)