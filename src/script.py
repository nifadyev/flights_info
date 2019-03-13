import argparse
# import datetime  # ? from datetime import datetime
import sys
from datetime import datetime, timedelta
import lxml.html
import requests

# TODO: change output method from horizontal to vertical table
# TODO: update README
# TODO: update imports to take only whats necessary
# ! max comment and docsting length is 72
# TODO: use paragraph indentation
# TODO: Add docstring for meta_flight_info

VALID_CITY_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

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

    dep_time = datetime.strptime(departure_time, "%H:%M")
    arr_time = datetime.strptime(arrival_time, "%H:%M")
    duration = timedelta(
        hours=arr_time.hour-dep_time.hour,
        minutes=arr_time.minute-dep_time.minute
    )

    hours = duration.seconds // 3600
    minutes = (duration.seconds - hours*3600) // 60
    formatted_hours = hours if hours>=10 else f"0{hours}"
    formatted_minutes = minutes if minutes >= 10 else f"0{minutes}"

    # TODO: possibly create datetime.time and return time.strftime
    return f"{formatted_hours}:{formatted_minutes}"

# ? Describe obvious args and its type
def check_route(dep_city, dest_city, flight_date):
    """Search route based of passed args in database.

    Raises:-
        KeyError -- unavailable route.
        KeyError -- no available flights for passed dates.
    """

    current_route = (dep_city, dest_city)

    if current_route not in DATES:
        available_routes = ",".join(f"({dep_city}, {dest_city})"
                                    for dep_city, dest_city in DATES)
        # available_routes = [f"({dep_city}, {dest_city})" for dep_city, dest_city in DATES]
        raise KeyError(f"Route not found. Available routes:{available_routes}")

    if flight_date.strftime("%d.%m.%Y") not in DATES[current_route]:
        message = "Flights for chosen dates not found. Available dates: "
        raise KeyError(message + ", ".join(DATES[current_route]))


def find_flight_info(arguments):
    """Handle arguments and search for available flights on flybulgarien.dk.

    Arguments:
        arguments {list} -- command line arguments.

    Returns:
        dict -- Available information about flights.
    """

    args = parse_arguments(arguments)

    try:
        check_route(args.dep_city, args.dest_city, args.dep_date)
        # if args.return_date:
        if args.return_date is not None:
            if args.dep_date > args.return_date:
                raise ValueError("Departure date is in the past "
                                 "in comparison with return date")

            check_route(args.dest_city, args.dep_city, args.return_date)
    except KeyError as key_error:
        # if args.verbose:
        if args.verbose is not None:
            raise key_error
        else:
            print(sys.exc_info()[1])
            sys.exit()

    response = requests.get("https://apps.penguin.bg/fly/quote3.aspx",
                            params=create_url_parameters(args))

    # TODO: handle An internal error occurred.
    # TODO: Please retry your request. on site
    # ? case for testing this try-except block
    try:
        html_page = lxml.html.document_fromstring(response.text)
    except ValueError:
        message = "Could not parse response, please try again. "
        # raise ValueError(message + (response.text if args.verbose
        #                             else "Use --verbose for more details."))
        # raise ValueError(message + (response.text if args.verbose is not None
        #                             else "Use --verbose for more details."))
        if args.verbose:
            raise ValueError(message + response.text)
        else:
            raise ValueError(message + "Use --verbose for more details.")

    # TODO: (optional) check network in firefox inspector and make get/post
    # TODO: requests to get necessary data
    # 0 element contains tbody => full table
    # ? content_table
    table = html_page.xpath("//table[@id='flywiz_tblQuotes']")[0]
    meta_info_about_flights = table.xpath("tr[contains(@id,'rinf')]")
    # meta_info_about_flights = table.xpath("./tr[contains(@id,'rinf')]")
    # IDs differ only in last 5 elements
    flight_ids = [item[-5:]
                  for item in table.xpath("./tr[contains(@id,'rinf')]/@id")]
    flights = dict(zip(flight_ids, meta_info_about_flights))

    flights_data = {}  # ? output_table

    # TODO: add useful comments for this cycle
    for flight_id, flight_info in flights.items():
        # flight_info[0] contains unnecessary info about radio button
        try:
            flight_date = datetime.strptime(flight_info[1].text,
                                            "%a, %d %b %y")
        except BaseException:
            raise ValueError("Could not correctly parse flight date.")

        # IATA city codes are at the end of flight_info[4].text
        dep_city = flight_info[4].text[-4:-1]
        dest_city = flight_info[5].text[-4:-1]

        if flight_date == args.dep_date and args.dep_city == dep_city\
                and args.dest_city == dest_city:
            # TODO: could be safely removed
            flight_infos = [
                item.text for item in flight_info]
            # flight_infos = [
            #     item.text for item in flight_info if item.text is not None]
            price_and_extra_info_unparsed = table.xpath(
                f"./tr[contains(@id,'{flight_id}') and not(contains(@id, 'rinf'))]/td[text()]")
            price_and_extra_info = [
                item.text for item in price_and_extra_info_unparsed]
            flights_data["Outbound"] = write_flight_information(flight_infos[1:],
                                                                price_and_extra_info,
                                                                args.persons)

        elif flight_date == args.return_date and args.dep_city in dest_city\
                and args.dest_city in dep_city:
            flight_infos = [
                item.text for item in flight_info if item.text is not None]
            # ! Inconsistent indentation
            price_and_extra_info_unparsed = table.xpath(
                f"./tr[contains(@id,'{flight_id}') and not(contains(@id, 'rinf'))]/td[text()]")
            # ! Inconsistent indentation
            price_and_extra_info = [
                item.text for item in price_and_extra_info_unparsed]
            flights_data["Inbound"] = write_flight_information(flight_infos,
                                                               price_and_extra_info,
                                                               args.persons)

    return flights_data


def parse_arguments(args):
    """Handle command line arguments using argparse.

    Arguments:
        args {list} -- command line arguments.

    Raises:
        argparse.ArgumentTypeError -- invalid argument type.

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
    argument_parser.add_argument("dep_date",
                                 help="departure flight date",
                                 type=validate_date)
    argument_parser.add_argument("persons",
                                 help="total number of persons",
                                 type=validate_persons)
    argument_parser.add_argument("-return_date",
                                 help="return flight date",
                                 type=validate_date)
    argument_parser.add_argument("-v", "--verbose",
                                 help="verbose output about errors",
                                 action='store_true')

    def raise_value_error(err_msg):
        raise argparse.ArgumentTypeError(err_msg)

    argument_parser.error = raise_value_error

    try:
        return argument_parser.parse_args(args)
    except BaseException:
        print(sys.exc_info()[1])
        sys.exit()


def create_url_parameters(args):
    """Create parameters for making get request.

    Arguments:
        args {argparse.Namespace} -- flight parameters.

    Returns:
        dict -- valid url parameters.
    """

    # ? namedtuple with asdict method
    if args.return_date is not None:
        return {
            "rt": "",
            "lang": "en",
            "depdate": args.dep_date.strftime("%d.%m.%Y"),
            "aptcode1": args.dep_city,
            "rtdate": args.return_date.strftime("%d.%m.%Y"),
            "aptcode2": args.dest_city,
            "paxcount": args.persons
        }

    return {
        "ow": "",
        "lang": "en",
        "depdate": args.dep_date.strftime("%d.%m.%Y"),
        "aptcode1": args.dep_city,
        "aptcode2": args.dest_city,
        "paxcount": args.persons
    }


def print_flights_information(flights_info):
    """Show information about flights.

    Arguments:
        flights_info {dict} -- parsed information about flights.
    """

    # Table header
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Direction", *flights_info["Outbound"].keys()))
    # Outbound flight
    print("{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Outbound", *flights_info["Outbound"].values()))
    # Inbound flight
    if "Inbound" in flights_info:
        # Last 7 chars of price contains currency and .00
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

    if code not in VALID_CITY_CODES:
        # raise argparse.ArgumentTypeError(
        #     "Invalid city code. Choose from this list: CPH, BLL, "
        #     "PDV, BOJ, SOF, VAR")
        f"Invalid city code. Choose from this list: {VALID_CITY_CODES}")

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

    parsed_date = datetime.strptime(flight_date, "%d.%m.%Y")

    if datetime.today() > parsed_date:
        raise argparse.ArgumentTypeError("Date in the past")

    return parsed_date


def validate_persons(persons):
    """Persons number validator.

    Arguments:
        persons {str} -- number of persons.

    Raises:
        TypeError -- cannot convert persons to int.
        argparse.ArgumentTypeError -- invalid type or not 0 < persons < 9.

    Returns:
        int -- valid persons number.
    """

    try:
        valid_persons = int(persons)
    except ValueError:
        raise TypeError("Invalid type of persons. Must be digit (1-8).")

    # if not 0 < valid_persons < 9:
    if valid_persons<1 or valid_persons>9:
    # if valid_persons not in range(1, 9):
        raise argparse.ArgumentTypeError("Invalid persons number. "
                                         "Max persons number: 8")

    return valid_persons

# TODO: pass args explicitly, meaning pass each arg of meta_flight_info separatly
def write_flight_information(meta_flight_info, price_and_extra_info, persons):
    """Parse flight information.

    Arguments:
        meta_flight_info {list} -- parsed from booking engine data.
        price_and_extra_info {list} -- price and additional information.
        persons {int} -- total number of people to book.

    Returns:
        dict -- parsed flight information.
    """

    # price_and_extra_info[0] contains extra "Price: " and "EUR"
    # Price without currency and label is in the middle
    total_cost = int(price_and_extra_info[0][7:-7]) * persons
    flight_duration = calculate_flight_duration(*meta_flight_info[1:3])
    # flight_duration = calculate_flight_duration(meta_flight_info[1],
    #                                               meta_flight_info[2])

    extra_info = price_and_extra_info[1] if len(
        price_and_extra_info) > 1 else ""

    # TODO: try namedtuple here
    # namedtuple._fields to get keys from tuple
    return {
        "Date": meta_flight_info[0],
        "Departure": meta_flight_info[1],
        "Arrival": meta_flight_info[2],
        "Flight duration": flight_duration,
        "From": meta_flight_info[3],
        "To": meta_flight_info[4],
        "Price": f"{total_cost}.00 EUR",
        "Additional information": extra_info
    }
