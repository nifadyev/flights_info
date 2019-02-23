import argparse
import datetime
import lxml.etree
import requests

# TODO: maybe divide this func to 4/5 separate ones
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
                                "17.07.2019", "24.07.2019", "31.07.2019",
                                "07.08.2019")
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
    if args[0] == "CPH" and args[1] == "BOJ":
        if ".".join(str_date) not in CPH_TO_BOJ_DATES:
            raise BaseException(f"No available flights from CPH to BOJ for date {'.'.join(str_date)}")
    if args[0] == "BLL" and args[1] == "BOJ":
        if ".".join(str_date) not in BLL_TO_BOJ_DATES:
            raise BaseException(f"No available flights for date {'.'.join(str_date)}")
    if args[0] == "BLL" and args[1] == "CPH":
        if ".".join(str_date) not in BLL_TO_CPH_DATES:
            raise BaseException(f"No available flights for date {'.'.join(str_date)}")
    if args[0] == "BOJ" and args[1] == "BLL":
        if ".".join(str_date) not in BOJ_TO_BLL_DATES:
            raise BaseException(f"No available flights for date {'.'.join(str_date)}")
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
        # args[4][:14] = "-return_date"
        return_date = tuple(i for i in args[4][13:].split("."))
        if args[0] == "CPH" and args[1] == "BOJ":
            if ".".join(return_date) not in BOJ_TO_CPH_DATES:
                raise BaseException(f"No available return flights for date {'.'.join(return_date)}")
        if args[0] == "BLL" and args[1] == "BOJ":
            if ".".join(return_date) not in BOJ_TO_BLL_DATES:
                raise BaseException(f"No available return flights for date {'.'.join(return_date)}")
        if args[0] == "BLL" and args[1] == "CPH":
            if ".".join(return_date) not in CPH_TO_BLL_DATES:
                raise BaseException(f"No available return flights for date {'.'.join(return_date)}")
        if args[0] == "BOJ" and args[1] == "BLL":
            if ".".join(return_date) not in BLL_TO_BOJ_DATES:
                raise BaseException(f"No available return flights for date {'.'.join(return_date)}")
        # Check return date
        # FIXME: probably unnecessary
        # current date format: yyyy-mm-dd
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
    # TODO: Wright correct description
    argument_parser = argparse.ArgumentParser(description="Flight informer")
    # TODO: add description of IATA codes
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


def calculate_flight_duration(departure_time, arrival_time):
    """ """

    parsed_departure_time = [int(i) for i in departure_time.split(":")]
    parsed_arrival_time = [int(i) for i in arrival_time.split(":")]

    minutes = parsed_arrival_time[1] - parsed_departure_time[1]
    correct_minutes = (60 + minutes) if minutes < 0 else minutes
    hours = parsed_arrival_time[0] - parsed_departure_time[0]
    correct_hours = hours - 1 if minutes < 0 else hours

    return (":".join([str(correct_hours) if correct_hours >= 10
                      else "".join(["0", str(correct_hours)]),
                      str(correct_minutes)] if correct_minutes >= 10
                     else "".join(["0", str(correct_minutes)])))


def parse_flight_date(date):
    parsed_date = list()
    # FIXME: do i really need unformat_date?!
    # unformat_date = date
    for item in date[5:].split(" "):
        if item == "Jun":
            parsed_date.append("06")
        elif item == "Jul":
            parsed_date.append("07")
        elif item == "Aug":
            parsed_date.append("08")
        elif item == "19":
            parsed_date.append("2019")
        else:
            parsed_date.append(
                "".join(["0", item]) if len(item) == 1 else item)

    return parsed_date

# TODO: change first arg cause request costs too much of time
def find_flight_info(args):
    """ """

    request = requests.get(create_url(args))
    if request.status_code != 200:
        # TODO: add proper comment
        raise ValueError("add proper comment")
    tree = lxml.etree.HTML(request.text)  # Full html page code
    table = tree.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # TODO: maybe this if is extra
    if table[1][0].text == "No available flights found.":
        # TODO: maybe need args to specify info
        print(f"Sorry, there is no available flight for this date")
        return

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<21}".format(
        "Direction",
        table[1][1].text, table[1][2].text, table[1][3].text,
        "Flight duration",
        table[1][4].text, table[1][5].text, "Price", "Additional information"))
    # Price is displayed per person
    # TODO: maybe change price to total cost or just remove adults arg
    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        # Empty row, with price, with price and additional info or with table2 header or with table2 name
        if len(table[row]) == 1 or len(table[row]) == 2\
                or len(table[row]) == 3 or table[row][1].text == "Date":
            continue

        flight_date = parse_flight_date(table[row][1].text)

        # Search for going out flight
        if ".".join(flight_date) == args.dep_date\
                and args.dep_city in table[row][4].text\
                and args.dest_city in table[row][5].text:
            print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<21}".format(
                "Going out",
                table[row][1].text, table[row][2].text, table[row][3].text,
                calculate_flight_duration(
                    table[row][2].text, table[row][3].text),
                table[row][4].text, table[row][5].text), end="")

            # First and second columns contains radio button and style
            # Row + 1 contains only price
            if len(table[row+1]) == 3:
                unformatted_price = table[row+1][1].text
                print("{:<13}".format(unformatted_price[8:]))
            # Row + 1 also contains additional information
            elif len(table[row+1]) == 4:
                unformatted_price = table[row+1][1].text
                print("{:<13} {:<20}".format(
                    unformatted_price[8:], table[row+1][2].text))

        # Search for coming back flight
        elif ".".join(flight_date) == args.return_date\
                and args.dest_city in table[row][4].text\
                and args.dep_city in table[row][5].text:
            print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<21}".format(
                "Coming back",
                table[row][1].text, table[row][2].text, table[row][3].text,
                calculate_flight_duration(
                    table[row][2].text, table[row][3].text),
                table[row][4].text, table[row][5].text), end="")

            if len(table[row+1]) == 3:
                unformatted_price = table[row+1][1].text
                print("{:<13}".format(unformatted_price[8:]))
            elif len(table[row+1]) == 4:
                unformatted_price = table[row+1][1].text
                print("{:<13} {:<20}".format(
                    unformatted_price[8:], table[row+1][2].text))
