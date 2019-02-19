import requests
# {
#   "lang": "en", 
#   "departure-city": "BLL",
#   "arrival-city": "BOJ".
#   "departure-date": 08.07.2019,
#   "adults-children": 1,
#  }

tickets = requests.get("https://apps.penguin.bg/fly/quote3.aspx?ow=&lang=en&depdate=03.07.2019&aptcode1=CPH&aptcode2=BOJ&paxcount=1&infcount=")
# tickets = requests.get("http://www.flybulgarien.dk/en/search?lang=2&departure-city=CPH&arrival-city=BOJ&reserve-type=&departure-date=26.06.2019&adults-children=1&search=Search%21")
print(tickets.status_code)
# print(tickets.content)