import argparse
import sys
from datetime import datetime, timedelta
import lxml.html
import requests


VALID_CITY_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

# All available routes and dates
DATES = {
    ("CPH", "BOJ"): {
        "26.06.2019", "03.07.2019", "10.07.2019", "17.07.2019", "24.07.2019",
        "31.07.2019", "07.08.2019"
    },
    ("BOJ", "CPH"): {
        "27.06.2019", "04.07.2019", "11.07.2019", "18.07.2019", "25.07.2019",
        "01.08.2019", "08.08.2019"
    },
    ("BOJ", "BLL"): {
        "01.07.2019", "08.07.2019", "15.07.2019", "22.07.2019", "29.07.2019",
        "05.08.2019"
    },
    ("BLL", "BOJ"): {
        "01.07.2019", "08.07.2019", "15.07.2019", "22.07.2019", "29.07.2019",
        "05.08.2019"
    }
}


def calculate_flight_duration(departure_time, arrival_time):
    """Calculate flight duration, max duration is 24:00.

    Arguments:
        departure_time {str} -- time of departing from departure city.
        arrival_time {str} -- time of arrival to destination city.

    Returns:
        str -- flight duration in format hh:mm.
    """

    dep_time = datetime.strptime(departure_time, "%H:%M")
    arr_time = datetime.strptime(arrival_time, "%H:%M")
    duration = timedelta(
        hours=arr_time.hour - dep_time.hour,
        minutes=arr_time.minute - dep_time.minute
    )

    hours = duration.seconds // 3600
    minutes = (duration.seconds - hours * 3600) // 60
    formatted_hours = hours if hours >= 10 else f"0{hours}"
    formatted_minutes = minutes if minutes >= 10 else f"0{minutes}"

    return f"{formatted_hours}:{formatted_minutes}"


def check_route(dep_city, dest_city, flight_date):
    """Search route based of passed args in database.

    Arguments:
        dep_city {str} -- departure city.
        dest_city {str} -- destination city.
        flight_date {datetime} -- date of current flight.
    Raises:
        KeyError -- unavailable route.
        KeyError -- no available flights for passed dates.
    """

    current_route = (dep_city, dest_city)

    if current_route not in DATES:
        available_routes = ",".join(
            f"({dep_city}, {dest_city})" for dep_city, dest_city in DATES
        )
        raise KeyError(f"Route not found. Available routes:{available_routes}")

    if flight_date.strftime("%d.%m.%Y") not in DATES[current_route]:
        message = "Flights for chosen dates not found. Available dates: "
        raise KeyError(message + ", ".join(DATES[current_route]))


def create_url_parameters(args):
    """Create parameters for making get request.

    Arguments:
        args {argparse.Namespace} -- flight parameters.

    Returns:
        dict -- valid url parameters.
    """

    parameters = {
        "rt": None,
        "ow": None,
        "lang": "en",
        "depdate": args.dep_date.strftime("%d.%m.%Y"),
        "aptcode1": args.dep_city,
        "rtdate": None,
        "aptcode2": args.dest_city,
        "paxcount": args.passengers
    }

    if args.return_date is not None:
        parameters["rt"] = ""
        parameters["rtdate"] = args.return_date.strftime("%d.%m.%Y")
    else:
        parameters["ow"] = ""

    return parameters


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
        if args.return_date is not None:
            if args.dep_date > args.return_date:
                raise ValueError(
                    "Departure date is in the past "
                    "in comparison with return date"
                )

            check_route(args.dest_city, args.dep_city, args.return_date)
    except KeyError as key_error:
        if args.verbose is not None:
            raise key_error
        else:
            print(sys.exc_info()[1])
            sys.exit()

    response = requests.get(
        "https://apps.penguin.bg/fly/quote3.aspx",
        params=create_url_parameters(args)
    )

    try:
        html_page = lxml.html.document_fromstring(response.text)
    except ValueError:
        message = "Could not parse response, please try again. "

        if args.verbose:
            raise ValueError(message + response.text)
        else:
            raise ValueError(message + "Use --verbose for more details.")

    # First element of the table contains tbody => full table
    table = html_page.xpath("//table[@id='flywiz_tblQuotes']")[0]
    meta_info_about_flights = table.xpath("tr[contains(@id,'rinf')]")
    # IDs differ only in last 5 elements
    flight_ids = [
        item[-5:] for item in table.xpath("./tr[contains(@id,'rinf')]/@id")
    ]
    flights = dict(zip(flight_ids, meta_info_about_flights))

    flights_data = {}

    for flight_id, flight_info in flights.items():
        # flight_info[0] contains unnecessary info about radio button
        try:
            flight_date = datetime.strptime(
                flight_info[1].text, "%a, %d %b %y"
            )
        except BaseException:
            raise ValueError("Could not correctly parse flight date.")

        # IATA city codes are at the end of flight_info[4].text
        dep_city = flight_info[4].text[-4:-1]
        dest_city = flight_info[5].text[-4:-1]

        if flight_date == args.dep_date and args.dep_city == dep_city\
                and args.dest_city == dest_city:
            # Parsed_flight_info list structure: info about radio button, date,
            # departure time, arrival time, departure city, destination city
            flights_data["Outbound"] = write_flight_information(
                *flight_info[1:], flight_id, table, args.passengers
            )
        elif flight_date == args.return_date and args.dep_city in dest_city\
                and args.dest_city in dep_city:
            flights_data["Inbound"] = write_flight_information(
                *flight_info[1:], flight_id, table, args.passengers
            )

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

    argument_parser.add_argument(
        "dep_city", help="departure city IATA code", type=validate_city_code
    )
    argument_parser.add_argument(
        "dest_city", help="destination city IATA code", type=validate_city_code
    )
    argument_parser.add_argument(
        "dep_date", help="departure flight date", type=validate_date
    )
    argument_parser.add_argument(
        "passengers", help="total number of passengers",
        type=validate_passengers
    )
    argument_parser.add_argument(
        "-return_date", help="return flight date", type=validate_date
    )
    argument_parser.add_argument(
        "-v", "--verbose", help="verbose output about errors",
        action='store_true'
    )

    def raise_value_error(err_msg):
        raise argparse.ArgumentTypeError(err_msg)

    argument_parser.error = raise_value_error

    try:
        return argument_parser.parse_args(args)
    except BaseException:
        print(sys.exc_info()[1])
        sys.exit()


def print_flights_information(flights_info):
    """Show information about flights.

    Arguments:
        flights_info {dict} -- parsed information about flights.
    """

    # Table header
    print(
        "{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Direction", *flights_info["Outbound"].keys())
    )
    # Outbound flight
    print(
        "{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
        ".format("Outbound", *flights_info["Outbound"].values())
    )
    # Inbound flight
    if "Inbound" in flights_info:
        # Last 7 chars of price contains ".00 EUR"
        total_cost = int(flights_info["Outbound"]["Price"][:-7])\
            + int(flights_info["Inbound"]["Price"][:-7])

        print(
            "{:<12} {:<17} {:<10} {:<10} {:<15} {:<20} {:<20} {:<13} {:<20}\
            ".format("Inbound", *flights_info["Inbound"].values())
        )
        print("{:<12} {:<10}".format("Total cost", f"{total_cost}.00 EUR"))


def validate_city_code(code):
    """Check whether city code is in VALID_CITY_DATES.

    Arguments:
        code {str} -- IATA city code.

    Raises:
        argparse.ArgumentTypeError -- code is not in VALID_CITY_CODES.

    Returns:
        str -- valid city code.
    """

    if code not in VALID_CITY_CODES:
        raise argparse.ArgumentTypeError(
            f"Invalid city code. Choose from this list: {VALID_CITY_CODES}"
        )

    return code


def validate_date(flight_date):
    """Validate flight date for correctness.

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


def validate_passengers(passengers):
    """Validate number of passengers.

    Arguments:
        passengers {str} -- number of passengers.

    Raises:
        TypeError -- cannot convert passengers to int.
        argparse.ArgumentTypeError -- invalid type or not 0 < passengers < 9.

    Returns:
        int -- valid passengers number.
    """

    try:
        valid_passengers = int(passengers)
    except ValueError:
        raise TypeError("Invalid type of passengers. Must be digit (1-8).")

    if valid_passengers < 1 or valid_passengers > 8:
        raise argparse.ArgumentTypeError(
            "Invalid passengers number. Max passengers number: 8"
        )

    return valid_passengers


def write_flight_information(
        date, dep_time, arr_time, dep_city, dest_city, flight_id, table,
        passengers
):
    """Parse flight information.
    Arguments:
        date {HtmlElement} -- flight date.
        dep_time {HtmlElement} -- departure time.
        arr_time {HtmlElement} -- arrival time.
        dep_city {HtmlElement} -- full departure city name and IATA code.
        dest_city {HtmlElement} -- full destination city name and IATA code.
        flight_id {str} -- ID of current flight.
        table {HtmlElement} -- table with full information about flights.
        passengers {int} -- total number passengers.
    Returns:
        dict -- parsed flight information.
    """

    price_and_extra_info = table.xpath(
        f"./tr[contains(@id,'{flight_id}')"
        "and not(contains(@id, 'rinf'))]/td[text()]"
    )
    price = price_and_extra_info[0].text
    extra_info = price_and_extra_info[1].text\
        if len(price_and_extra_info) > 1 else ""

    # price_and_extra_info[0] contains extra "Price: " and "EUR"
    total_cost = int(price[7:-7]) * passengers
    flight_duration = calculate_flight_duration(
        dep_time.text, arr_time.text
    )

    return {
        "Date": date.text,
        "Departure": dep_time.text,
        "Arrival": arr_time.text,
        "Flight duration": flight_duration,
        "From": dep_city.text,
        "To": dest_city.text,
        "Price": f"{total_cost}.00 EUR",
        "Additional information": extra_info
    }
