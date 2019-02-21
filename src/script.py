import argparse
import datetime
import lxml.etree


def check_arguments(args):
    """ """
    date = tuple(int(i) for i in args[2].split("."))
    str_date = tuple(i for i in args[2].split("."))
    now = datetime.datetime.now()

    AVAILABLE_ROUTES = (("CPH", "BOJ"), ("BLL", "BOJ"), ("BOJ", "CPH"),
                        ("BOJ", "BLL"))
    CITY_CODES = ("CPH", "BLL", "PDV", "BOJ", "SOF", "VAR")

    # Check flight routes
    if args[0] not in CITY_CODES:
        raise ValueError(f"City code {args[0]} is not in the base")
    elif args[1] not in CITY_CODES:
        raise ValueError(f"City code {args[0]} is not in the base")
    elif (args[0], args[1]) not in AVAILABLE_ROUTES:
        raise ValueError(f"Flight route {args[0]}-{args[1]} is unavailable")
    elif args[0] == args[1]:
        raise ValueError(
            "Departure city and destination city cannot be the same")

    # Check date
    # Date is already past
    if str(now.date()) > "-".join(str_date[::-1]):
        raise ValueError
    # Invalid day, month or year
    if date[0] < 1 or date[0] > 31 or date[1] < 1\
            or date[1] > 12 or date[2] < 2019:
        raise ValueError

    if len(args) == 5:
        return_date = tuple(i for i in args[4].split("."))
        # Check return date
        if str(now.date()) > "-".join(str_date[::-1]):
            raise ValueError
        elif "-".join(str_date[::-1]) >= "-".join(return_date[::-1]):
            raise ValueError
    # TODO: add check for equal dest_city and dep_city


def parse_arguments(args):
    """ """
    # try:
    #     check_arguments(args)
    # except:

    # else:
    check_arguments(args)

    argument_parser = argparse.ArgumentParser()
    # TODO: add description of IATA codes
    # TODO: create dict with impossible flights combination
    # (also includes the same from to city)
    argument_parser.add_argument("dep_city",
                                 help="departure city IATA code",
                                 choices=["CPH", "BLL", "PDV", "BOJ",
                                          "SOF", "VAR"])
    argument_parser.add_argument("dest_city",
                                 help="destination city IATA code",
                                 choices=["CPH", "BLL", "PDV", "BOJ",
                                          "SOF", "VAR"])
    argument_parser.add_argument("dep_date", help="departure flight date")
    argument_parser.add_argument("adults_children",
                                 help="Number of adults and children")
    argument_parser.add_argument("-return_date", help="return flight date")

    return argument_parser.parse_args(args)


def create_url(args):
    """ """
    # try:
    #     return f"https://apps.penguin.bg/fly/quote3.aspx?"\
    #             f"{'rt=' if args.return_date else 'ow='}"\
    #             f"&lang=en&depdate={args.dep_date}&aptcode1={args.dep_city}"\
    #             f"{f'&rtdate={args.return_date}' if args.return_date else ''}"\
    #             f"&aptcode2={args.dest_city}&paxcount={args.adults_children}&infcount="
    # except:

    # else:
    return f"https://apps.penguin.bg/fly/quote3.aspx?"\
        f"{'rt=' if args.return_date else 'ow='}"\
        f"&lang=en&depdate={args.dep_date}&aptcode1={args.dep_city}"\
        f"{f'&rtdate={args.return_date}' if args.return_date else ''}"\
        f"&aptcode2={args.dest_city}&paxcount={args.adults_children}&infcount="


def find_flight_info(request):
    """ """
    tree = lxml.etree.HTML(request.text)  # Full html page code
    table = tree.xpath(
        f"/html/body/form[@id='form1']/div/table[@id='flywiz']"
        f"/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # Table header
    print("{:<17} {:<10} {:<10} {:<20} {:<20} {:<13} {:<21}".format(
        table[1][1].text, table[1][2].text, table[1][3].text,
        table[1][4].text, table[1][5].text, "Price", "Additional information"))
    # Price is displayed per person
    # TODO: maybe change price to total cost or just remove adults arg

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
            print("{:<17} {:<10} {:<10} {:<20} {:<21}".format(
                current_row[0], current_row[1], current_row[2],
                current_row[3], current_row[4]), end="")
        # Row with price
        elif len(current_row) == 1:
            print("{:<13}".format(current_row[0][8:]))
        elif len(current_row) == 2:
            print("{:<13} {:<20}".format(current_row[0][8:], current_row[1]))
