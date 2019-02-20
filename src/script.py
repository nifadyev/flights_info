# import requests
import lxml.etree


def find_flight_info(request):
    # TODO: how deep tree is may differ depending from type of flight (return or not)
    tree = lxml.etree.HTML(request.text)
    row = 3  # TODO: check this value for one way flight
    # tbody is not used in xpath (return empty list)
    table = tree.xpath(
        f"/html/body/form[@id='form1']/div/table[@id='flywiz']/tr/td/table[@id='flywiz_tblQuotes']/tr")
    # print(len(table))

    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        current_row = list()
        # First and second columns contains radio button and style
        for column in range(1, len(table[row])):
            if table[row][column].text:
                current_row.append(table[row][column].text)
        print(" ".join(current_row))
