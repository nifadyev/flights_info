import argparse
import datetime
import lxml.etree
import requests

# TODO: decorate main func flight_info by check_args and create_url
# TODO: output info if one of the args data or return date is invalid


def validate_date(dep_date, return_date):
    """Validate departure date and return date.
    Check whether these dates are correctly formatted and not outdated.
    """

    date = tuple(int(i) for i in dep_date.split("."))
    str_date = tuple(i for i in dep_date.split("."))
    # current date format: yyyy-mm-dd
    formatted_date = "-".join(str_date[::-1])
    current_date = str(datetime.datetime.now().date())

    # yyyy-mm-dd
    if len(formatted_date) != 10:
        raise ValueError("Invalid date format")

    # Date is already past
    if current_date > formatted_date:
        raise ValueError("Flight date has past")

    # Invalid day, month or year
    if date[0] < 1 or date[0] > 31:
        raise ValueError("Invalid day")
    elif date[1] < 1 or date[1] > 12:
        raise ValueError("Invalid month")
    elif date[2] != 2019:
        raise ValueError("Invalid year")

    # Check return date
    if return_date:
        ret_date = tuple(int(i) for i in return_date.split("."))
        str_ret_date = tuple(i for i in return_date.split("."))
        formatted_ret_date = "-".join(str_ret_date[::-1])

        if len(formatted_date) != 10:
            raise ValueError("Invalid date format")

        # Invalid day, month or year
        if ret_date[0] < 1 or ret_date[0] > 31:
            raise ValueError("Invalid day")
        elif ret_date[1] < 1 or ret_date[1] > 12:
            raise ValueError("Invalid month")
        elif ret_date[2] != 2019:
            raise ValueError("Invalid year")

        if current_date > formatted_ret_date:
            raise ValueError("Return flight date is outdated")
        elif formatted_date >= formatted_ret_date:
            raise ValueError("Return date cannot be earlier than flight date")


def check_date_availability(args):
    """Check flight availability for current departure date and return date."""

    # Available flight dates for each possible route
    CPH_TO_BOJ_DATES = ("26.06.2019", "03.07.2019", "10.07.2019",
                        "17.07.2019", "24.07.2019", "31.07.2019",
                        "07.08.2019")
    BOJ_TO_CPH_DATES = ("27.06.2019", "04.07.2019", "11.07.2019",
                        "18.07.2019", "25.07.2019", "01.08.2019",
                        "08.08.2019")
    BOJ_TO_BLL_DATES = ("01.07.2019", "08.07.2019", "15.07.2019",
                        "22.07.2019", "29.07.2019", "05.08.2019")
    BLL_TO_BOJ_DATES = ("01.07.2019", "08.07.2019", "15.07.2019",
                        "22.07.2019", "29.07.2019", "05.08.2019")

    # TODO: later make a func out of it to decrease code size and duplicity
    # Check going out routes
    if args.dep_city == "CPH" and args.dest_city == "BOJ":
        if args.dep_date not in CPH_TO_BOJ_DATES:
            raise BaseException(
                f"No available flights from CPH to BOJ for date\
                 {args.dep_date}")
    if args.dep_city == "BLL" and args.dest_city == "BOJ":
        if args.dep_date not in BLL_TO_BOJ_DATES:
            raise BaseException(
                f"No available flights for date {args.dep_date}")
    if args.dep_city == "BOJ" and args.dest_city == "CPH":
        if args.dep_date not in BOJ_TO_CPH_DATES:
            raise BaseException(
                f"No available flights for date {args.dep_date}")
    if args.dep_city == "BOJ" and args.dest_city == "BLL":
        if args.dep_date not in BOJ_TO_BLL_DATES:
            raise BaseException(
                f"No available flights for date {args.dep_date}")

    # Check coming back routes
    if args.return_date:
        if args.dep_city == "CPH" and args.dest_city == "BOJ":
            if args.return_date not in BOJ_TO_CPH_DATES:
                raise BaseException(
                    f"No available return flights for date\
                     {args.return_date}")
        if args.dep_city == "BLL" and args.dest_city == "BOJ":
            if args.return_date not in BOJ_TO_BLL_DATES:
                raise BaseException(
                    f"No available return flights for date {args.return_date}")
        if args.dep_city == "BOJ" and args.dest_city == "CPH":
            if args.return_date not in CPH_TO_BOJ_DATES:
                raise BaseException(
                    f"No available return flights for date {args.return_date}")
        if args.dep_city == "BOJ" and args.dest_city == "BLL":
            if args.return_date not in BLL_TO_BOJ_DATES:
                raise BaseException(
                    f"No available return flights for date {args.return_date}")


def check_route(dep_city, dest_city):
    """Check current route for flight availability.
    Also check if departure city and destination city are equal.
    """

    AVAILABLE_ROUTES = (("CPH", "BOJ"), ("BLL", "BOJ"), ("BOJ", "CPH"),
                        ("BOJ", "BLL"))

    if dep_city == dest_city:
        raise ValueError("Same departure city and destination city")
    elif (dep_city, dest_city) not in AVAILABLE_ROUTES:
        raise ValueError("Unavailable route")


def parse_arguments(args):
    """Parse command line arguments using aprgparse.
    Contains help message.
    """

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
    argument_parser.add_argument("dep_date", help="departure flight date",)
    argument_parser.add_argument("adults_children",
                                 help="Number of adults and children")
    argument_parser.add_argument("-return_date", help="return flight date")

    return argument_parser.parse_args(args)


def create_url(args):
    """Create valid url for making a request booking engine."""

    return f"https://apps.penguin.bg/fly/quote3.aspx?"\
        f"{'rt=' if args.return_date else 'ow='}"\
        f"&lang=en&depdate={args.dep_date}&aptcode1={args.dep_city}"\
        f"{f'&rtdate={args.return_date}' if args.return_date else ''}"\
        f"&aptcode2={args.dest_city}&paxcount={args.adults_children}&infcount="

# TODO: def print_info()


def calculate_flight_duration(departure_time, arrival_time):
    """Calculate flight dureatiom in format hh:mm."""

    # FIXME: invalid value for return flight BOJ BLL
    parsed_departure_time = [int(i) for i in departure_time.split(":")]
    parsed_arrival_time = [int(i) for i in arrival_time.split(":")]

    minutes = parsed_arrival_time[1] - parsed_departure_time[1]
    correct_minutes = (60 + minutes) if minutes < 0 else minutes
    hours = parsed_arrival_time[0] - parsed_departure_time[0]
    correct_hours = (hours - 1) if minutes < 0 else hours

    return (":".join([str(correct_hours) if correct_hours >= 10
                      else "".join(["0", str(correct_hours)]),
                      str(correct_minutes)] if correct_minutes >= 10
                     else "".join(["0", str(correct_minutes)])))


def parse_flight_date(date):
    """Parse date to format dd.mm.yyyy."""

    parsed_date = list()

    # First 5 chars of date contain weekday
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

    return ".".join(parsed_date)


def find_flight_info(arguments):
    """Main function."""

    # Check city codes
    # FIXME: argparse throw an error. How to avoid this?
    try:
        args = parse_arguments(arguments)
    except SystemExit:
        raise SystemExit(
            "Please choose IATA city codes from suggested above list")

    try:
        validate_date(
            args.dep_date, args.return_date if args.return_date else None)
    except ValueError as value_error:
        raise SystemExit("Invalid date", args.dep_date)

    try:
        check_date_availability(args)
    except ValueError as value_error:
        raise SystemExit("Unchecked date")
        # Check route for availability
    try:
        check_route(args.dep_city, args.dest_city)
    except ValueError as value_error:
        if value_error.args[0] == "Same departure city and destination city":
            raise SystemExit(
                f"Departure city and destination city must differ,\
                  please try again")
        elif value_error.args[0] == "Unavailable route":
            raise SystemExit(
                f"Route {args.dep_city}-{args.dest_city} is unavailable,\
                  please choose one from these: ")

    request = requests.get(create_url(args))
    if request.status_code != 200:
        raise ValueError("Invalid request")
    tree = lxml.etree.HTML(request.text)  # Full html page code
    table = tree.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<21}\
        ".format(
        "Direction",
        table[1][1].text, table[1][2].text, table[1][3].text,
        "Flight duration",
        table[1][4].text, table[1][5].text, "Price", "Additional information"))
    # Price is displayed per person
    # TODO: maybe change price to total cost or just remove adults arg
    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        # Empty row, with price, with price and additional info or with table2
        # header or with table2 name
        if len(table[row]) == 1 or len(table[row]) == 2\
                or len(table[row]) == 3 or table[row][1].text == "Date":
            continue

        flight_date = parse_flight_date(table[row][1].text)

        # Search for going out flight
        if flight_date == args.dep_date\
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
        elif flight_date == args.return_date\
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
