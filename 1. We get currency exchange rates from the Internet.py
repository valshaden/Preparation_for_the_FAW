# 1. Получаем курсы валют из интернета
# https://open.er-api.com/v6/latest/USD

##import requests
##import json
##result = requests.get('https://open.er-api.com/v6/latest/USD')
##data = json.loads(result.text)
##print(data)

# Выводим красиво с помощью PrettyPrinter

import requests
import json
import pprint

result = requests.get('https://open.er-api.com/v6/latest/USD')
data = json.loads(result.text)
# настраиваем PrettyPrinter
p = pprint.PrettyPrinter(indent=4)  # indent=4 - значит отступ в 4 пробела
p.pprint(data)  # "красиво" выводим на экран данные
