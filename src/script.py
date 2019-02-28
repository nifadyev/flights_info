import argparse
import datetime
import lxml.etree
import lxml.objectify
import requests
import collections

# TODO: decorate main func flight_info by check_args and create_url
# TODO: change names going out and coming back to outbound and inbound


def calculate_flight_duration(departure_time, arrival_time):
    """Return flight duration in format hh:mm."""

    dep_time = datetime.datetime.strptime(departure_time, "%H:%M")
    arr_time = datetime.datetime.strptime(arrival_time, "%H:%M")
    duration = datetime.timedelta(hours=arr_time.hour - dep_time.hour,
                                  minutes=arr_time.minute - dep_time.minute)

    return str(duration)[:-3]


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


def check_date_availability(args, two_way_trip):
    """Check flight availability for specified date."""

    # Available flight dates for each possible route
    departure_city = args.dest_city if two_way_trip else args.dep_city
    destination_city = args.dep_city if two_way_trip else args.dest_city
    date = args.return_date if two_way_trip else args.dep_date

    # Check dates
    if date not in DATES[(departure_city, destination_city)]:
        raise KeyError(f"No available flights for date {date}")


def check_route(dep_city, dest_city):
    """Raise KeyError if route is not in DATES."""

    # Only these routes are available
    if (dep_city, dest_city) not in DATES:
        raise KeyError("Unavailable route")


def find_flight_info(arguments):
    # TODO: Modify docstring
    """Search for available flights and output found info to console."""

    args = validate_input_data(arguments)
    request = requests.get("https://apps.penguin.bg/fly/quote3.aspx?",
                           params=parse_url_parameters(args))

    if request.text:
        tree = lxml.etree.HTML(request.text)
    else:
        raise ValueError("Request body is empty")

    table = tree.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # Flight = collections.namedtuple("Flight", "Date, Departure, Arrival,\
    # Flight duration, From, To, Price, Additional information")

    flights_data = {"Going Out": {"Date": "", "Departure": "",
                                  "Arrival": "", "Flight duration": "",
                                  "From": "", "To": "", "Price": "",
                                  "Additional information": ""},
                    "Coming back": {"Date": "", "Departure": "",
                                    "Arrival": "", "Flight duration": "",
                                    "From": "", "To": "", "Price": "",
                                    "Additional information": ""}}

    for row in table:
        # TODO: if len == 3 then write data from this row to sum structure
        # and then call func write...
        if 1 <= len(row) <= 3 or row[1].text == "Date":
            # if len(row) == 3:
                # extra_info = (row[1].text[8:] if row[1].text else "",
                #                    row[2].text if row[2].text else "")
                # print(extra_info)
                # print(next(iter(table)).type)
            continue
        # print(len(row))

        # # ? Could it be simplified
        # flight_date = datetime.datetime.strptime(
        #     table[row][1].text[5:], "%d %b %y").strftime("%d.%m.%Y")

        # # Search for going out flight
        # # table[row][4:5].text contains city name and city code => in
        # if flight_date == args.dep_date\
        #         and args.dep_city in table[row][4].text\
        #         and args.dest_city in table[row][5].text:
        # TODO: Save row here and during next iteraion call write...
        #     write_flight_information(
        #         flights_data["Going Out"], table[row], table[row+1])
        #     # going_out = Flight()
        #     # write_flight_information(
        #     #     Flight, table[row], table[row+1])

        # elif flight_date == args.return_date\
        #         and args.dest_city in table[row][4].text\
        #         and args.dep_city in table[row][5].text:
        #     write_flight_information(
        #         flights_data["Coming back"], table[row], table[row+1])

    # TODO: maybe change price to total cost or just remove adults arg
    # First and second table rows contains table name and names of columns
    for row in range(2, len(table)):
        # Empty row, with price, with price and additional info or with table2
        # header or with table2 name
        if 1 <= len(table[row]) <= 3 or table[row][1].text == "Date":
            continue

        # ? Could it be simplified
        flight_date = datetime.datetime.strptime(
            table[row][1].text[5:], "%d %b %y").strftime("%d.%m.%Y")

        # Search for going out flight
        # table[row][4:5].text contains city name and city code => in
        if flight_date == args.dep_date\
                and args.dep_city in table[row][4].text\
                and args.dest_city in table[row][5].text:
            write_flight_information(
                flights_data["Going Out"], table[row], table[row+1])
            # going_out = Flight()
            # write_flight_information(
            #     Flight, table[row], table[row+1])

        elif flight_date == args.return_date\
                and args.dest_city in table[row][4].text\
                and args.dep_city in table[row][5].text:
            write_flight_information(
                flights_data["Coming back"], table[row], table[row+1])

    print_flights_information(flights_data)


def parse_arguments(args):
    """Parse command line arguments using argparse.
    Contain help message.
    """

    argument_parser = argparse.ArgumentParser(description="Flight informer")

    argument_parser.add_argument("dep_city",
                                 help="departure city IATA code",
                                 type=validate_city_code)
    argument_parser.add_argument("dest_city",
                                 help="destination city IATA code",
                                 type=validate_city_code)
    argument_parser.add_argument("dep_date", help="departure flight date",)
    argument_parser.add_argument("adults_children",
                                 help="Number of adults and children")
    argument_parser.add_argument("-return_date", help="return flight date")

    return argument_parser.parse_args(args)


def parse_url_parameters(args):
    """Return valid url parameters for requests.get method."""

    result = {"rt" if args.return_date else "ow": "", "lang": "en",
              "depdate": args.dep_date,
              "aptcode1": args.dep_city, "rtdate": args.return_date,
              "aptcode2": args.dest_city, "paxcount": args.adults_children}

    if not args.return_date:
        del result["rtdate"]

    return result


def print_flights_information(flights_info):
    """Output table containing inforamtion about flights."""

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<21}\
        ".format("Direction", *flights_info["Going Out"].keys()))

    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Going Out", *flights_info["Going Out"].values()))
    # Two-way trip
    if flights_info["Coming back"]["Date"]:
        print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
            ".format("Coming back", *flights_info["Coming back"].values()))


def validate_city_code(code):
    """Raise ArgumentError if city code isn't in VALID_CITY_CODES.

    Return city code.
    """

    VALID_CITY_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

    if code not in VALID_CITY_CODES:
        raise argparse.ArgumentTypeError("Invalid city code")

    return code

# TODO: change this to validate_dates to check whether inbound date is earlier than outbound
# TODO: read skype: check date type in type argpares.add_argument
# TODO: but here also check flight dates


def validate_date(flight_date):
    """Raise ValueError if date is invalid or in the past."""

    # ? Why reversed is needed
    # TODO: use datetime methods instead of tuple
    # print(parsed_dates)
    parsed_dates = datetime.datetime.strptime(flight_date, "%d.%m.%Y").strftime("%d.%m.%Y")
    parsed_date = tuple(int(i) for i in flight_date.split("."))
    # current date format: dd.mm.yyyy

    # TODO: move *reversed(parsed_date) to separate variable
    try:
        datetime.date(*reversed(parsed_date)).strftime("%d.%m.%Y")
    except ValueError as value_error:
        raise ValueError(f"{value_error.args[0]}. Please enter valid date")

    if datetime.date.today().strftime("%d.%m.%Y") > datetime.date(*reversed(parsed_date)):
        raise ValueError("Date in the past")


def validate_input_data(arguments):
    """ Validate all input arguments.
    Raise exceptions if they are invalid.

    Return parsed arguments. 
    """
    # Check city codes
    args = parse_arguments(arguments)
    validate_date(args.dep_date)
    check_date_availability(args, False)
    # Check route for availability
    check_route(args.dep_city, args.dest_city)
    if args.return_date:
        validate_date(args.return_date)
        check_date_availability(args, True)

    return args


def write_flight_information(dest, flight_info, extra_flight_info):
    """Write flight information to dest data structure (dict)."""
    # TODO: modify docstring: describe args
    # TODO: rename i or get rid of it
    i = 1
    # TODO: create list with result values and unpack it in Flight namedtuple
    # Flight._make(iterable)
    for key in dest:
        if key == "Flight duration":
            dest[key] = calculate_flight_duration(
                flight_info[2].text, flight_info[3].text)
        # Price is displayed per person
        elif key == "Price" and extra_flight_info[1].text:
            # table[row+1][1].text[0:9] = "Price = "
            dest[key] = extra_flight_info[1].text[8:]
        # Row + 1 also contains additional information
        # eg. NO_LUGGAGE_INCLUDED
        elif key == "Additional information" and extra_flight_info[2].text:
            dest[key] = extra_flight_info[2].text
        elif i < 6:
            dest[key] = flight_info[i].text if flight_info[i].text else ""
            i += 1
