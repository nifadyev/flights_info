import argparse
import datetime
import lxml.html
import requests

# TODO: change output method from horizontal to vertical table
# TODO: change max persons to 8
# class Networkerror(RuntimeError):
#    def __init__(self, arg):
#       self.args = arg

# try:
#    raise Networkerror("Bad hostname")
# except Networkerror,e:
#    print e.args

# TODO: добавить ключ -v в параметры, где будет verbose вывод ошибок. 
# в таком случае можно тут вывести request.text например, 
# для удобного дебага, или текст пойманного исключения
# except ValueError as e:
#     msg = 'Could not parse response body. '
#     if '-v' in args:
#         msg += request.text  # тот случай, когда += мб оправдан
#     raise ValueError(msg)
# All available routes and dates
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


def calculate_flight_duration(departure_time, arrival_time):
    """Calculate flight duration.

    Returns:
        str -- flight duration in format hh:mm.
    """

    dep_time = datetime.datetime.strptime(departure_time, "%H:%M")
    arr_time = datetime.datetime.strptime(arrival_time, "%H:%M")
    duration = datetime.timedelta(hours=arr_time.hour-dep_time.hour,
                                  minutes=arr_time.minute-dep_time.minute)

    hours = duration.seconds // 3600
    minutes = (duration.seconds - hours * 3600) // 60
    formatted_hours = hours if hours >= 10 else f"0{hours}"
    formatted_minutes = minutes if minutes >= 10 else f"0{minutes}"

    # TODO: possibly create datetime.time and return time.strftime
    return f"{formatted_hours}:{formatted_minutes}"


def check_route(dep_city, dest_city, flight_date, prev_flight_date):
    """Search route based of passed args in database.

    Arguments:
        dep_city -- departure city.
        dest_city -- destination city.
        flight_date -- flight_date for route dep_city-dest_city
        prev_flight_date -- past flight_date for route dest_city-dep_city

    Raises:
        ValueError -- departure date is in the past
        KeyError -- unavailable route
        KeyError -- no available flights for passed dates
    """
    # TODO: move this to separate func and also add diff check
    # between dep_date and return_date (more info in skype)
    if prev_flight_date and prev_flight_date > flight_date:
        raise ValueError("Departure date is in the past "
                         "in comparison with return date")

    if (dep_city, dest_city) not in DATES:
        raise KeyError("Unavailable route")

    if flight_date.strftime("%d.%m.%Y") not in DATES[(dep_city, dest_city)]:
        raise KeyError("No available flights for chosen dates")


def find_flight_info(arguments):
    """Handle arguments and search for available flights on flybulgarien.dk.

    Arguments:
        arguments {list} -- command line arguments

    Returns:
        dict -- Available information about flights.
    """

    args = parse_arguments(arguments)
    check_route(args.dep_city, args.dest_city, args.dep_date, None)
    if args.return_date:
        check_route(args.dest_city, args.dep_city,
                    args.return_date, args.dep_date)
    request = requests.get("https://apps.penguin.bg/fly/quote3.aspx",
                           params=parse_url_parameters(args))
    # TODO: handle An internal error occurred.
    # TODO: Please retry your request. on site
    # ? case for testing this try-except block
    try:
        html = lxml.html.document_fromstring(request.text)
        print(html)
    except ValueError:
        raise ValueError("Response body is empty")

    table = html.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")

    # flights_data = {"Outbound": 0, "Inbound": 0}
    flights_data = dict()
    flight_info = list()
    # TODO: add useful comments for this cycle
    for row in table:
        if 1 <= len(row) <= 3 or row[1].text == "Date":
            if len(row) == 3 and flight_info:
                # row[1].text[:9]="Price = "
                flight_info.append(row[1].text[8:] if row[1].text else "")
                flight_info.append(row[2].text if row[2].text else "")
                direction = "Outbound" if outbound_flight else "Inbound"

                flights_data[direction] = write_flight_information(
                    flight_info, args.persons)

                flight_info = None
            continue

        # row[1].text[:6] contains weekday
        flight_date = datetime.datetime.strptime(row[1].text[5:], "%d %b %y")

        # row[4:5].text contains city name and city code => in
        if flight_date == args.dep_date and args.dep_city in row[4].text\
                and args.dest_city in row[5].text:

            flight_info = [item.text for item in row]
            outbound_flight = True
        elif flight_date == args.return_date and args.dest_city in row[4].text\
                and args.dep_city in row[5].text:

            flight_info = [item.text for item in row]
            outbound_flight = False

    return flights_data

# def error(self, message):
#     """error(message: string)

#     Prints a usage message incorporating the message to stderr and
#     exits.

#     If you override this in a subclass, it should not return -- it
#     should either exit or raise an exception.
#     """
#     self.print_usage(_sys.stderr)
#     args = {'prog': self.prog, 'message': message}
#     self.exit(2, _('%(prog)s: error: %(message)s\n') % args)


def parse_arguments(args):
    """Handle command line arguments using argparse.

    Arguments:
        args {[type]} -- [description]

    Raises:
        argparse.ArgumentTypeError -- invalid argument type

    Returns:
        argparse.Namespace -- parsed arguments of valid type.
    """

    argument_parser = argparse.ArgumentParser(description="Flight informer")

    argument_parser.add_argument("dep_city",
                                 help="departure city IATA code",
                                 type=validate_city_code)
    argument_parser.add_argument("dest_city",
                                 help="destination city IATA code",
                                 type=validate_city_code)
    # TODO: show list of available codes
    # TODO: add helping tips for user
    argument_parser.add_argument("dep_date", help="departure flight date",
                                 type=validate_date)
    argument_parser.add_argument("persons",
                                 help="total number of persons",
                                 type=validate_persons)
    argument_parser.add_argument("-return_date", help="return flight date",
                                 type=validate_date)
    # TODO: add new optional arg verbose for verbose error output and traceback
    # and without it just an error message

    # ? what's better: pretty error message by argparse but ugly test output
    # ? or full exception traceback but pretty test output
    def raise_value_error(err_msg):
        raise argparse.ArgumentTypeError(err_msg)

    argument_parser.error = raise_value_error

    return argument_parser.parse_args(args)


def parse_url_parameters(args):
    """Create parameters for making get request.

    Arguments:
        args {argparse.Namespace} -- flight parameters.

    Returns:
        dict -- valid url parameters.
    """

    parameters = {"rt" if args.return_date else "ow": "", "lang": "en",
                  "depdate": args.dep_date.strftime("%d.%m.%Y"),
                  "aptcode1": args.dep_city,
                  "rtdate": args.return_date.strftime("%d.%m.%Y")
                  if args.return_date else "",
                  "aptcode2": args.dest_city, "paxcount": args.persons}

    if not args.return_date:
        del parameters["rtdate"]

    return parameters


def print_flights_information(flights_info):
    """Show information about flights.

    Arguments:
        flights_info {dict} -- parsed information about flights.
    """

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<21}\
        ".format("Direction", *flights_info["Outbound"].keys()))
    # Outbound flight
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Outbound", *flights_info["Outbound"].values()))
    # Inbound flight
    # if flights_info["Inbound"]:
    if "Inbound" in flights_info:
        # Last 7 char of price contains currency
        total_cost = int(flights_info["Outbound"]["Price"][:-7])\
            + int(flights_info["Inbound"]["Price"][:-7])

        print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
            ".format("Inbound", *flights_info["Inbound"].values()))
        print("{:<12} {:<10}".format("Total cost", f"{total_cost}.00 EUR"))


def validate_city_code(code):
    """City code validator.

    Arguments:
        code {str} -- IATA city code.

    Raises:
        argparse.ArgumentTypeError -- code is not in VALID_CITY_CODES

    Returns:
        str -- valid city code.
    """

    VALID_CITY_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

    if code not in VALID_CITY_CODES:
        raise argparse.ArgumentTypeError("Invalid city code "
                                         "Choose from this list: CPH, BLL, PDV, BOJ, SOF, VAR")

    return code


def validate_date(flight_date):
    """Flight date validator.

    Arguments:
        flight_date {str} -- date of flight.

    Raises:
        ValueError -- invalid date or date is in the past.

    Returns:
        datetime.datetime -- valid flight date.
    """

    parsed_date = datetime.datetime.strptime(
        flight_date, "%d.%m.%Y")

    if datetime.datetime.today() > parsed_date:
        # raise ValueError("Date in the past")
        raise argparse.ArgumentTypeError("Date in the past")

    return parsed_date


def validate_persons(persons):
    """Persons number validator.

    Arguments:
        persons {str} -- number of persons.

    Raises:
        TypeError -- cannot convert persons to int.
        argparse.ArgumentTypeError -- invalid type or not 0 < persons < 10.

    Returns:
        int -- valid persons number.
    """

    try:
        valid_persons = int(persons)
    except ValueError:
        raise TypeError("Invalid type of persons. Must be digit (1-9).")

    if not 0 < valid_persons < 10:
        raise argparse.ArgumentTypeError("Invalid persons number. "
                                         "Max persons number: 9")

    return valid_persons


def write_flight_information(raw_flight_info, persons):
    """Parse flight information.

    Arguments:
        raw_flight_info {list} -- parsed from booking engine data.
        persons {int} -- total number of people to book.

    Returns:
        dict -- parsed flight information.
    """
    # TODO: use namedtupl   e instead of dict
    filled_flight_info = {"Date": "", "Departure": "",
                          "Arrival": "", "Flight duration": "",
                          "From": "", "To": "", "Price": "",
                          "Additional information": ""}
    i = 1

    for key in filled_flight_info:
        if key == "Flight duration":
            filled_flight_info[key] = calculate_flight_duration(
                raw_flight_info[2], raw_flight_info[3])
        # Element before last contains price
        elif key == "Price" and raw_flight_info[-2]:
            # extra_route_info[0][-6:] contains currency
            total_cost = int(raw_flight_info[-2][:-7]) * persons
            filled_flight_info[key] = f"{total_cost}.00 EUR"
        # Last elemcontains additional information (eg. NO_LUGGAGE_INCLUDED)
        elif key == "Additional information" and raw_flight_info[-1]:
            filled_flight_info[key] = raw_flight_info[-1]
        elif i < 6:
            filled_flight_info[key] = raw_flight_info[i]\
                if raw_flight_info[i] else ""
            i += 1

    return filled_flight_info
