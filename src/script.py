# import requests
import lxml.etree
import pprint


def find_flight_info(request):
    # TODO: how deep tree is may differ depending from type of flight (return or not)
    tree = lxml.etree.HTML(request.text)
    row = 3  # TODO: check this value for one way flight
    # tbody is not used in xpath (return empty list)
    table = tree.xpath(
        f"/html/body/form[@id='form1']/div/table[@id='flywiz']/tr/td/table[@id='flywiz_tblQuotes']/tr")

    print("{:<15} {:<10} {:<10} {:<20} {:<20} {:<20}".format(
        table[1][1].text, table[1][2].text, table[1][3].text, table[1][4].text, table[1][5].text, "Price"))
    # TODO: if data is not available then request will return closest flight
    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        current_row = list()
        if len(table[row]) == 1:
            continue
        elif "Date" == table[row][1].text:
            continue
        # print("row_number", row)
        # First and second columns contains radio button and style
        for column in range(1, len(table[row])):
            if table[row][column].text:
                current_row.append(table[row][column].text)
        # for item in current_row:
        #     print("%10s" % item, end="")
        # print()
        # print(" ".join(current_row))
        # print(len(current_row))
        if len(current_row) == 5:
            print("{:<15} {:<10} {:<10} {:<20} {:<21}".format(
                current_row[0], current_row[1], current_row[2], current_row[3], current_row[4]), end="")
        elif len(current_row) == 1:
            print("{:<20}".format(current_row[0][8:]))
        else:
            print(" ".join(current_row))