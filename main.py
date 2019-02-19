import requests
import lxml.etree



# tickets = requests.get("https://apps.penguin.bg/fly/quote3.aspx?ow=&lang=en&depdate=03.07.2019&aptcode1=CPH&aptcode2=BOJ&paxcount=1&infcount=")
# tickets = requests.get("http://www.flybulgarien.dk/en/search?lang=2&departure-city=CPH&arrival-city=BOJ&reserve-type=&departure-date=26.06.2019&adults-children=1&search=Search%21")
# print(tickets.status_code)
# print(tickets.content)

search_results = requests.get("https://apps.penguin.bg/fly/quote3.aspx?rt=&lang=en&depdate=08.07.2019&aptcode1=BLL&rtdate=15.07.2019&aptcode2=BOJ&paxcount=2&infcount=")
print(search_results.status_code)
# print(search_results.text)
tree = lxml.etree.HTML(search_results.text)
# TODO: how deep tree is may differ depending from type of flight (return or not)
# table = tree.xpath("/html/body/form[@id='form1']/div/table[@id='flywiz']")
# table = tree.xpath("/html/body/form[@id='form1']/div/table[@id='flywiz']/tr/td/table[@id='flywiz_tblQuotes']")

# print(table[0][0][0].text)
# # print(table.tag)
# # First and second tr contains table name and names of columns
# # First and second td contains radio button and style
# for info in table[0][2]:
#     print(info.text)
row = 3
table = tree.xpath(f"/html/body/form[@id='form1']/div/table[@id='flywiz']/tr/td/table[@id='flywiz_tblQuotes']/tr[{row}]")

print(table)
print(table[0].tag)
# First and second tr contains table name and names of columns
# First and second td contains radio button and style
for info in table[0]:
    print(info.text)
