import argparse
import datetime
import lxml.etree
import requests

# TODO: decorate main func flight_info by check_args and create_url
# TODO: output info if one of the args data or return date is invalid


# TODO: Sort func by name

def validate_date(flight_date):
    """Check whether date is correctly formatted and not old."""

    date = tuple(int(i) for i in flight_date.split("."))
    str_date = tuple(i for i in flight_date.split("."))
    # current date format: yyyy-mm-dd
    formatted_date = "-".join(str_date[::-1])
    current_date = str(datetime.datetime.now().date())

    # yyyy-mm-dd
    if len(formatted_date) != 10:
        raise ValueError("Invalid date format")

    # Invalid day, month or year
    if date[0] < 1 or date[0] > 31 or date[1] < 1 or date[1] > 12\
            or date[2] != 2019:
        raise ValueError("Invalid date format")

    # Date is already past
    if current_date > formatted_date:
        raise ValueError("Date in the past")


def check_date_availability(args, is_return_flight):
    """Check flight availability for specified date."""

    # Available flight dates for each possible route
    DATES = {("CPH", "BOJ"): {"26.06.2019", "03.07.2019", "10.07.2019",
                              "17.07.2019", "24.07.2019", "31.07.2019",
                              "07.08.2019"},
             ("BOJ", "CPH"): {"27.06.2019", "04.07.2019", "11.07.2019",
                              "18.07.2019", "25.07.2019", "01.08.2019",
                              "08.08.2019"},
             ("BOJ", "BLL"): {"01.07.2019", "08.07.2019", "15.07.2019",
                              "22.07.2019", "29.07.2019", "05.08.2019"},
             ("BLL", "BOJ"): {"01.07.2019", "08.07.2019", "15.07.2019",
                              "22.07.2019", "29.07.2019", "05.08.2019"}}

    departure_city = args.dest_city if is_return_flight else args.dep_city
    destination_city = args.dep_city if is_return_flight else args.dest_city
    date = args.return_date if is_return_flight else args.dep_date

    # Check dates
    if date not in DATES[(departure_city, destination_city)]:
        raise ValueError(f"No available flights for date {date}")


def check_route(dep_city, dest_city):
    """Check current route for flight availability.
    Also check if departure city and destination city are equal.
    """

    ROUTES = {("CPH", "BOJ"), ("BLL", "BOJ"), ("BOJ", "CPH"),
              ("BOJ", "BLL")}

    if dep_city == dest_city:
        raise ValueError("Same departure city and destination city")
    elif (dep_city, dest_city) not in ROUTES:
        raise ValueError("Unavailable route")


# TODO: add description of IATA codes
def validate_city_code(code):
    VALID_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}
    if code not in VALID_CODES:
        raise ValueError("Invalid city code")


def parse_arguments(args):
    """Parse command line arguments using argparse.
    Contains help message.
    """

    argument_parser = argparse.ArgumentParser(description="Flight informer")

    argument_parser.add_argument("dep_city",
                                 help="departure city IATA code")
    argument_parser.add_argument("dest_city",
                                 help="destination city IATA code")
    argument_parser.add_argument("dep_date", help="departure flight date",)
    argument_parser.add_argument("adults_children",
                                 help="Number of adults and children")
    argument_parser.add_argument("-return_date", help="return flight date")

    return argument_parser.parse_args(args)


def parse_url_parameters(args):
    """Create valid url parameters for making a request
     to Flybulgarien booking engine.

     Returns url parameters.
     """

    if args.return_date:
        return {"rt": "", "lang": "en", "depdate": args.dep_date,
                "aptcode1": args.dep_city, "rtdate": args.return_date,
                "aptcode2": args.dest_city, "paxcount": args.adults_children}

    return {"ow": "", "lang": "en", "depdate": args.dep_date,
            "aptcode1": args.dep_city, "aptcode2": args.dest_city,
            "paxcount": args.adults_children}


def calculate_flight_duration(departure_time, arrival_time):
    """Calculate flight duration in format hh:mm.

       Returns time in format hh:mm.
    """

    parsed_departure_time = tuple(int(i) for i in departure_time.split(":"))
    parsed_arrival_time = tuple(int(i) for i in arrival_time.split(":"))

    minutes = parsed_arrival_time[1] - parsed_departure_time[1]
    hours = parsed_arrival_time[0] - parsed_departure_time[0]
    correct_minutes = (60 + minutes) if minutes < 0 else minutes
    correct_hours = (hours - 1) if minutes < 0 else hours

    duration = [str(correct_hours) if correct_hours >= 10
                else f"0{correct_hours}",
                str(correct_minutes) if correct_minutes >= 10
                else f"0{correct_minutes}"]

    return ":".join(duration)

# TODO: get rid of it when replace it with internal method from datetime


def validate_input_data(arguments):
    # Check city codes
    # FIXME: argparse throw an error. How to avoid this?
    args = parse_arguments(arguments)
    validate_city_code(args.dep_city)
    validate_city_code(args.dest_city)
    validate_date(args.dep_date)
    check_date_availability(args, False)
    # Check route for availability
    check_route(args.dep_city, args.dest_city)
    if args.return_date:
        validate_date(args.return_date)
        check_date_availability(args, True)

    return args

# TODO: fill here specials struct (namedtuple or dict) and then in separate func print info


def find_flight_info(arguments):
    """Main function."""

    args = validate_input_data(arguments)
    request = requests.get("https://apps.penguin.bg/fly/quote3.aspx?",
                           parse_url_parameters(args))
    # try:
    #     text = request.text
    # if request.text:
    # tree = lxml.etree.HTML(request.text)
    # else:
    # raise ValueError("Request body is empty")
    tree = lxml.etree.HTML(request.text)  # Full html page code
    # TODO: read about diff between HTML and Objectify
    # TODO: handle exc here
    table = tree.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<21}\
        ".format("Direction", table[1][1].text, table[1][2].text,
                 table[1][3].text, "Flight duration", table[1][4].text,
                 table[1][5].text, "Price", "Additional information"))
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
                # table[row+1][1].text[0:9] = "Price = "
                print("{:<13}".format(table[row+1][1].text[8:]))
            # Row + 1 also contains additional information
            # eg. NO_LUGGAGE_INCLUDED
            elif len(table[row+1]) == 4:
                print("{:<13} {:<20}".format(
                    table[row+1][1].text[8:], table[row+1][2].text))

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
                print("{:<13}".format(table[row+1][1].text[8:]))
            elif len(table[row+1]) == 4:
                print("{:<13} {:<20}".format(
                    table[row+1][1].text[8:], table[row+1][2].text))


def parse_flight_date(date):
    """Parse date to format dd.mm.yyyy."""

    parsed_date = list()

    # First 5 chars of date contain weekday
    for item in date[5:].split(" "):
        # TODO: inspect datetime
        if item == "Jun":
            parsed_date.append("06")
        elif item == "Jul":
            parsed_date.append("07")
        elif item == "Aug":
            parsed_date.append("08")
        elif item == "19":
            parsed_date.append("2019")
        else:
            # Day format: dd
            parsed_date.append(
                "".join(["0", item]) if len(item) == 1 else item)

    return ".".join(parsed_date)
