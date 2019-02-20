# import requests
import lxml.etree


def find_flight_info(request, two_way):
    # TODO: how deep tree is may differ depending from type of flight (return or not)
    tree = lxml.etree.HTML(request.text)
    # First and second tr contains table name and names of columns
    # First and second td contains radio button and style
    row = 3  # TODO: check this value for one way flight
    # tbody is not used in xpath (return empty list)
    table = tree.xpath(
        f"/html/body/form[@id='form1']/div/table[@id='flywiz']/tr/td/table[@id='flywiz_tblQuotes']/tr")
    # print(len(table))
    # print(table[2][1].text)
    
    # for info in table[0]:
    #     print(info.text)

    for row in range(2, len(table)):
        current_row = list()
        for column in range(1, len(table[row])):
            if table[row][column].text:
                current_row.append(table[row][column].text)
            # print(table[row][column].text)
        print(" ".join(current_row))
        # for item in table[row]:
        #     print(item.text)
    # if two_way:
    #     print("two way")

    # else:
    #     print("one way")

