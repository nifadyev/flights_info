import argparse
import datetime
import lxml.etree
import requests

# TODO: Handle cases where there is no flight info
# TODO: find it in prev commits (case: persons= -2)
# TODO: define custom exception (optional)
# TODO: globally change docstrings to the one in write...

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

    # Don't need to check args because its assumed that they're valid
    dep_time = datetime.datetime.strptime(departure_time, "%H:%M")
    arr_time = datetime.datetime.strptime(arrival_time, "%H:%M")
    duration = datetime.timedelta(hours=arr_time.hour-dep_time.hour,
                                  minutes=arr_time.minute-dep_time.minute)

    hours = duration.seconds // 3600
    minutes = (duration.seconds - hours * 3600) // 60
    formatted_hours = hours if hours >= 10 else f"0{hours}"
    formatted_minutes = minutes if minutes >= 10 else f"0{minutes}"

    return f"{formatted_hours}:{formatted_minutes}"


def check_route(dep_city, dest_city, dep_date, return_date):
    """Search route based of passed args in database. 

    Raises:
        ValueError -- departure date is in the past
        KeyError -- unavailable route
        KeyError -- no available flights for passed dates
    """
    # ? leave as it is or call check_route(dep_city, dest_city, return_date, dep_date)
    # ? in find_flight_info to remove duplicity but decrease tests readability
    if return_date:
        if dep_date > return_date:
            raise ValueError("Departure date is in the past "
                             "in comparison with return date")
        if return_date.strftime("%d.%m.%Y") not in DATES[(dep_city, dest_city)]:
            raise KeyError("No return for chosen dates")

    if (dep_city, dest_city) not in DATES:
        raise KeyError("Unavailable route")

    if dep_date.strftime("%d.%m.%Y") not in DATES[(dep_city, dest_city)]:
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
                    args.dep_date, args.return_date)
    request = requests.get("https://apps.penguin.bg/fly/quote3.aspx",
                           params=parse_url_parameters(args))
    # TODO: handle An internal error occurred.
    # TODO: Please retry your request. on site
    # ? case for testing this try-except block
    try:
        tree = lxml.etree.HTML(request.text)
    except ValueError:
        raise ValueError("Request body is empty")

    table = tree.xpath(
        "/html/body/form[@id='form1']/div/table[@id='flywiz']"
        "/tr/td/table[@id='flywiz_tblQuotes']/tr")

    flights_data = {"Outbound": 0, "Inbound": 0}

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
    argument_parser.add_argument("dep_date", help="departure flight date",
                                 type=validate_date)
    argument_parser.add_argument("persons",
                                 help="total number of persons",
                                 type=validate_persons)
    argument_parser.add_argument("-return_date", help="return flight date",
                                 type=validate_date)

    # ? what's better: pretty error message by argparse but ugly test output
    # ? or full exception traceback but pretty test output
    def raise_value_error(err_msg):
        raise argparse.ArgumentTypeError(err_msg)

    argument_parser.error = raise_value_error

    return argument_parser.parse_args(args)


def parse_url_parameters(args):
    """Return valid url parameters for requests.get method."""

    if args.return_date:
        return {"rt" if args.return_date else "ow": "", "lang": "en",
                "depdate": args.dep_date.strftime("%d.%m.%Y"),
                "aptcode1": args.dep_city,
                "rtdate": args.return_date.strftime("%d.%m.%Y"),
                "aptcode2": args.dest_city, "paxcount": args.persons}
    else:
        return {"rt" if args.return_date else "ow": "", "lang": "en",
                "depdate": args.dep_date.strftime("%d.%m.%Y"),
                "aptcode1": args.dep_city,
                "aptcode2": args.dest_city, "paxcount": args.persons}


def print_flights_information(flights_info):
    """Print information about flights."""

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<21}\
        ".format("Direction", *flights_info["Outbound"].keys()))
    # Outbound flight
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Outbound", *flights_info["Outbound"].values()))
    # Inbound flight
    if flights_info["Inbound"]:
        total_cost = int(flights_info["Outbound"]["Price"][:-7])\
            + int(flights_info["Inbound"]["Price"][:-7])

        print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
            ".format("Inbound", *flights_info["Inbound"].values()))
        print("{:<12} {:<10}".format("Total cost", f"{total_cost}.00 EUR"))


def validate_city_code(code):
    """Raise ArgumentError if city code isn't in VALID_CITY_CODES.

    Return city code.
    """

    VALID_CITY_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

    if code not in VALID_CITY_CODES:
        raise argparse.ArgumentTypeError("Invalid city code")

    return code


def validate_date(flight_date):
    """Raise ValueError if date is invalid or in the past.

    Return valid date.
    """

    parsed_date = datetime.datetime.strptime(
        flight_date, "%d.%m.%Y")

    if datetime.datetime.today() > parsed_date:
        raise ValueError("Date in the past")

    return parsed_date


def validate_persons(persons):
    """ """
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

    filled_flight_info = {"Date": "", "Departure": "",
                          "Arrival": "", "Flight duration": "",
                          "From": "", "To": "", "Price": "",
                          "Additional information": ""}
    i = 1

    for key in filled_flight_info:
        if key == "Flight duration":
            filled_flight_info[key] = calculate_flight_duration(
                raw_flight_info[2], raw_flight_info[3])
        elif key == "Price" and raw_flight_info[-2]:
            # extra_route_info[0][-6:] contains currency
            total_cost = int(raw_flight_info[-2][:-7]) * persons
            filled_flight_info[key] = f"{total_cost}.00 EUR"
        # Row+1 also contains additional information (eg. NO_LUGGAGE_INCLUDED)
        elif key == "Additional information" and raw_flight_info[-1]:
            filled_flight_info[key] = raw_flight_info[-1]
        elif i < 6:
            filled_flight_info[key] = raw_flight_info[i]\
                if raw_flight_info[i] else ""
            i += 1

    return filled_flight_info
