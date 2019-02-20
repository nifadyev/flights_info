import lxml.etree

# TODO: add def print info


def find_flight_info(request):
    """ """
    tree = lxml.etree.HTML(request.text)  # Full html page code
    table = tree.xpath(
        f"/html/body/form[@id='form1']/div/table[@id='flywiz']"
        f"/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # Table header
    print("{:<15} {:<10} {:<10} {:<20} {:<20} {:<20}".format(
        table[1][1].text, table[1][2].text, table[1][3].text,
        table[1][4].text, table[1][5].text, "Price"))

    # TODO: if data is not available then request will return closest flight
    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        current_row = list()

        # Remove empty string from output
        if len(table[row]) == 1:
            continue
        # Remove return flight table header if there is one
        # TODO: do not remove it cause this is another table for return flights
        elif table[row][1].text == "Date":
            continue

        # First and second columns contains radio button and style
        for column in range(1, len(table[row])):
            if table[row][column].text:
                current_row.append(table[row][column].text)

        if len(current_row) == 5:
            print("{:<15} {:<10} {:<10} {:<20} {:<21}".format(
                current_row[0], current_row[1], current_row[2],
                current_row[3], current_row[4]), end="")
        # Row with price
        elif len(current_row) == 1:
            print("{:<20}".format(current_row[0][8:]))
