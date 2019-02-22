import argparse
import datetime
import lxml.etree

# TODO: maybe divide this func to 4/5 separate ones
# TODO: exclude from output extra cities and flights with extra dates
# TODO: захардкодить доступные для полета даты
# TODO: decorate main func flight_info by check_args and create_url
# TODO: output info if one of the args data or return date is invalid


def check_arguments(args):
    """ """
    CPH_TO_BOJ_DATES = ("26.06.2019", "03.07.2019", "10.07.2019",
                        "17.07.2019", "24.07.2019", "31.07.2019", "07.08.2019")
    BLL_TO_BOJ_DATES = ("01.07.2019", "08.07.2019", "15.07.2019",
                        "22.07.2019", "29.07.2019", "05.08.2019")
    # FIXME: info on calendar is not the same as searched info
    BOJ_TO_CPH_DATES = ("27.06.2019", "04.07.2019", "11.07.2019",
                        "18.07.2019", "25.07.2019", "01.08.2019", "08.08.2019")
    BOJ_TO_CPH_DATES_INVALID = ("26.06.2019", "03.07.2019", "10.07.2019",
                        "17.07.2019", "24.07.2019", "31.07.2019", "07.08.2019")
    BOJ_TO_BLL_DATES = ("01.07.2019", "08.07.2019", "15.07.2019",
                        "22.07.2019", "29.07.2019", "05.08.2019")

    date = tuple(int(i) for i in args[2].split("."))
    str_date = tuple(i for i in args[2].split("."))
    current_date = str(datetime.datetime.now().date())

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
    if current_date > "-".join(str_date[::-1]):
        raise ValueError("Flight date has past")
    # Invalid day, month or year
    elif date[0] < 1 or date[0] > 31:
        raise ValueError("Invalid day")
    elif date[1] < 1 or date[1] > 12:
        raise ValueError("Invalid month")
    elif date[2] != 2019:
        raise ValueError("Invalid year")

    # Return date is set
    if len(args) == 5:
        return_date = tuple(i for i in args[4].split("."))
        # Check return date
        # FIXME: probably unnecessary
        if current_date > "-".join(return_date[::-1]):
            raise ValueError("Return flight date is outdated")
        elif "-".join(str_date[::-1]) >= "-".join(return_date[::-1]):
            raise ValueError("Return date cannot be earlier than flight date")


def parse_arguments(args):
    """ """
    # try:
    #     check_arguments(args)
    # except:
    # except ValueError, e:
    # raise ValueError(f"Flight route {args[0]}-{args[1]} is unavailable")
    # then print that this flight is unavailable without request

    # else:
    # TODO: maybe reimagine this func to accept already parsed by argparse args
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

    return f"https://apps.penguin.bg/fly/quote3.aspx?"\
        f"{'rt=' if args.return_date else 'ow='}"\
        f"&lang=en&depdate={args.dep_date}&aptcode1={args.dep_city}"\
        f"{f'&rtdate={args.return_date}' if args.return_date else ''}"\
        f"&aptcode2={args.dest_city}&paxcount={args.adults_children}&infcount="

# TODO: def print_info()


def find_flight_info(request, args):
    """ """
    tree = lxml.etree.HTML(request.text)  # Full html page code
    table = tree.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")
    if table[1][0].text == "No available flights found.":
        # TODO: maybe need args to specify info
        print(f"Sorry, there is no available flight for this date")
        return
    # TODO: add column with flight duration
    # Table header
    # TODO: move Going out and Coming back to the left => change string format
    print(f"\t\t\t\t\t{table[0][0].text}")
    print("{:<17} {:<10} {:<10} {:<20} {:<20} {:<13} {:<21}".format(
        table[1][1].text, table[1][2].text, table[1][3].text,
        table[1][4].text, table[1][5].text, "Price", "Additional information"))
    # Price is displayed per person
    # TODO: maybe change price to total cost or just remove adults arg

    # TODO: if data is not available then request will return closest flight
    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        if len(table[row]) == 1 or len(table[row]) == 2 or len(table[row]) == 3 or table[row][1].text == "Date":
            continue
            
        flight_date = list()
        unformat_date = table[row][1].text
        for item in unformat_date[5:].split(" "):
            if item == "Jun":
                flight_date.append("06")
            elif item == "Jul":
                flight_date.append("07")
            elif item == "Aug":
                flight_date.append("08")
            elif item == "19":
                flight_date.append("2019")
            else:
                flight_date.append("".join(["0", item]) if len(item) == 1 else item)
        # print(".".join(flight_date))
        if ".".join(flight_date) == args.return_date:
            print("Alright")

        current_row = list()
        # if ".".join(flight_date) == args.dep_date and args.dep_city in table[row][4].text and args.dest_city in table[row][5]:
        #     print price and additional info here
        #     if len(table[row+1]) == 1:
        #         only price
        #     elif len(table[row+ 1]) == 2:
        #         price + additional info
        #     OK
        # elif table[row][1].text == args.return_date and args.dest_city in table[row][4].text and args.dep_city in table[row][5]:
        #     OK
        if ".".join(flight_date) == args.dep_date and args.dep_city in table[row][4].text and args.dest_city in table[row][5].text:
            print("{:<17} {:<10} {:<10} {:<20} {:<21}".format(
                table[row][1].text, table[row][2].text, table[row][3].text,
                table[row][4].text, table[row][5].text), end="")
            if len(table[row+1]) == 3:
                # print("HRERE")
                unformatted_price = table[row+1][1].text
                print("{:<13}".format(unformatted_price[8:]))
            elif len(table[row+1]) == 4:
                # print("HRsadERE")
                unformatted_price = table[row+1][1].text
                # print(table[row+1][2].text)
                print("{:<13} {:<20}".format(unformatted_price[8:], table[row+1][2].text))
        elif ".".join(flight_date) == args.return_date and args.dest_city in table[row][4].text and args.dep_city in table[row][5].text:
            print("{:<17} {:<10} {:<10} {:<20} {:<21}".format(
                table[row][1].text, table[row][2].text, table[row][3].text,
                table[row][4].text, table[row][5].text), end="")
            if len(table[row+1]) == 3:
                # print("HRERE")
                unformatted_price = table[row+1][1].text
                print("{:<13}".format(unformatted_price[8:]))
            elif len(table[row+1]) == 4:
                # print("HRsadERE")
                unformatted_price = table[row+1][1].text
                # print(table[row+1][2].text)
                print("{:<13} {:<20}".format(unformatted_price[8:], table[row+1][2].text))
        # Remove empty string from output
        # if len(table[row]) == 1:
        #     continue
        # # Table header
        # elif table[row][1].text == "Date":
        #     print("\n\t\t\t\t\tComing back")
        #     # print("{:<17} {:<10} {:<10} {:<20} {:<20} {:<13} {:<21}".format(
        #     #     table[1][1].text, table[1][2].text, table[1][3].text,
        #     #     table[1][4].text, table[1][5].text, "Price",
        #     #     "Additional information"))
        #     continue

        # # First and second columns contains radio button and style
        # for column in range(1, len(table[row])):
        #     if table[row][column].text:
        #         current_row.append(table[row][column].text)

        # if len(current_row) == 5:
        #     print("{:<17} {:<10} {:<10} {:<20} {:<21}".format(
        #         current_row[0], current_row[1], current_row[2],
        #         current_row[3], current_row[4]), end="")

        # # Row with price
        # elif len(current_row) == 1:
        #     print("{:<13}".format(current_row[0][8:]))
        # # + additional information
        # elif len(current_row) == 2:
        #     print("{:<13} {:<20}".format(current_row[0][8:], current_row[1]))
