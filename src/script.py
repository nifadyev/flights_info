import argparse
import datetime
import lxml.html
import lxml.etree
import lxml.objectify
import requests
import sys

# TODO: change output method from horizontal to vertical table
# class Networkerror(RuntimeError):
#    def __init__(self, arg):
#       self.args = arg

# try:
#    raise Networkerror("Bad hostname")
# except Networkerror,e:
#    print e.args


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


def check_route(dep_city, dest_city, flight_date):
    """Search route based of passed args in database.

    Arguments:
        dep_city -- departure city.
        dest_city -- destination city.
        flight_date -- flight_date for route dep_city-dest_city.

    Raises:
        KeyError -- unavailable route.
        KeyError -- no available flights for passed dates.
    """

    if (dep_city, dest_city) not in DATES:
        available_routes = ",".join(f"({dep_city}, {dest_city})"
                                    for dep_city, dest_city in DATES)
        raise KeyError(f"Route not found. Available routes:{available_routes}")

    if flight_date.strftime("%d.%m.%Y") not in DATES[(dep_city, dest_city)]:
        message = "Flights for chosen dates not found. Available dates: "
        raise KeyError(message + ", ".join(DATES[(dep_city, dest_city)]))


def find_flight_info(arguments):
    """Handle arguments and search for available flights on flybulgarien.dk.

    Arguments:
        arguments {list} -- command line arguments

    Returns:
        dict -- Available information about flights.
    """

    args = parse_arguments(arguments)

    try:
        check_route(args.dep_city, args.dest_city, args.dep_date)
        if args.return_date:
            if args.dep_date > args.return_date:
                raise ValueError("Departure date is in the past "
                                 "in comparison with return date")

            check_route(args.dest_city, args.dep_city, args.return_date)
    except KeyError as e:
        if args.verbose:
            raise e
        else:
            print(sys.exc_info()[1])
            sys.exit()

    request = requests.get("https://apps.penguin.bg/fly/quote3.aspx",
                           params=create_url_parameters(args))

    # TODO: handle An internal error occurred.
    # TODO: Please retry your request. on site
    # ? case for testing this try-except block
    try:
        # html = lxml.html.document_fromstring(request.text)
        html = lxml.etree.HTML(request.text)
    except ValueError:
        message = "Could not parse response, please try again. "
        if args.verbose:
            raise ValueError(message + request.text)
        else:
            raise ValueError(message + "Use --verbose for more details.")
    # TODO: take only table and do subrequests to it by another xpath
    # ! how to differentiate rows with main info and row with price
    # ! search in table for trs with tds contining input atr
    # ! then save meta data about flight AND arg of onclick=selectedRow()
    # ! then again search in table for  tr with saved arg to get price and add info
    table = html.xpath("//table[@id='flywiz_tblQuotes']/tr/td[text()]")
    # table = html.xpath(
    #     "/html/body/form[@id='form1']/div/table[@id='flywiz']"
    #     "/tr/td/table[@id='flywiz_tblQuotes']")

    table_list = html.xpath("//table[@id='flywiz_tblQuotes']")
    # table_list = html.xpath("/html/body/form[@id='form1']/div/table[@id='flywiz']"
    #     "/tr/td/table[@id='flywiz_tblQuotes']")[0]
    # print(type(table_list),type(table_list[0]), len(table_list))
    # table_tree = lxml.etree.HTML(table_list)
    # print(html.get_element_by_id("flywiz*"))
    # ! valid solution but choose button is included
    # temp = table_list[0].xpath("./tr[contains(@id,'rinf')]")
    # meta_info_about_flights = table_list[0].xpath("./tr[contains(@id,'rinf')]/td[not(position()=1)]")
    meta_info_about_flights = table_list[0].xpath("./tr[contains(@id,'rinf')]")
    # Remove all info about radio button 
    for row in meta_info_about_flights:
        row.remove(row[0])

        # print(row.xpath("./td/input")[0])
    print(len(meta_info_about_flights[0]), meta_info_about_flights[0][0].text)
    # flight_ids = meta_info_about_flights[0].xpath("../tr[contains(@id,'rinf')]/@id")
    flight_ids = table_list[0].xpath("./tr[contains(@id,'rinf')]/@id")
    print(type(flight_ids[0]), len(flight_ids))
    outbound_price_and_extra_info = table_list[0].xpath(f"./tr[contains(@id,'{flight_ids[0][-5:]}') and not(contains(@id, 'rinf'))]")
    # temp2 = temp[0].xpath("./td[text()]")
    # print(request.text)
    print(meta_info_about_flights)
    print(flight_ids[0], flight_ids[0][-5:])
    print(len(meta_info_about_flights))
    for i in outbound_price_and_extra_info:
        print(i[1].text)
    print(len(outbound_price_and_extra_info))
    # print(meta_info_about_flights[0][0].text)
    # print(type(table_list))
    # print(type(request.text))
    sys.exit(0)
    i = 0
    # flights_data = dict()
    flights_data = {}
    # TODO: add useful comments for this cycle
    while i < len(table):
        try:
            flight_date = datetime.datetime.strptime(table[i].text,
                                                     "%a, %d %b %y")
        except BaseException:
            raise ValueError("Could not correctly parse flight date. "
                             "Table does not contain date.")

        if flight_date == args.dep_date and args.dep_city in table[i+3].text\
                and args.dest_city in table[i+4].text:

            # i - i+6 table elements contain info about 1 flight
            flight_info = [cell.text for cell in table[i:i+6]]
            flights_data["Outbound"] = write_flight_information(flight_info,
                                                                args.persons)
        elif args.return_date and flight_date == args.return_date\
                and args.dep_city in table[i+4].text\
                and args.dest_city in table[i+3].text:

            flight_info = [cell.text for cell in table[i:i+6]]
            flights_data["Inbound"] = write_flight_information(flight_info,
                                                               args.persons)

        i += 6

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
    argument_parser.add_argument("dep_date", help="departure flight date",
                                 type=validate_date)
    argument_parser.add_argument("persons",
                                 help="total number of persons",
                                 type=validate_persons)
    argument_parser.add_argument("-return_date", help="return flight date",
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
    # TODO: get rid of 3 if statements
    # parameters = {"rt" if args.return_date else "ow": "", "lang": "en",
    #               "depdate": args.dep_date.strftime("%d.%m.%Y"),
    #               "aptcode1": args.dep_city,
    #               "rtdate": args.return_date.strftime("%d.%m.%Y")
    #               if args.return_date else "",
    #               "aptcode2": args.dest_city, "paxcount": args.persons}

    # if not args.return_date:
    #     del parameters["rtdate"]

    # return parameters
    if args.return_date:
        return {"rt": "", "lang": "en",
                "depdate": args.dep_date.strftime("%d.%m.%Y"),
                "aptcode1": args.dep_city,
                "rtdate": args.return_date.strftime("%d.%m.%Y"),
                "aptcode2": args.dest_city, "paxcount": args.persons}

    return {"ow": "", "lang": "en",
            "depdate": args.dep_date.strftime("%d.%m.%Y"),
            "aptcode1": args.dep_city,
            "aptcode2": args.dest_city, "paxcount": args.persons}


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
        raise argparse.ArgumentTypeError(
            "Invalid city code. Choose from this list: CPH, BLL, "
            "PDV, BOJ, SOF, VAR")

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

    if not 0 < valid_persons < 9:
        raise argparse.ArgumentTypeError("Invalid persons number. "
                                         "Max persons number: 8")

    return valid_persons


def write_flight_information(raw_flight_info, persons):
    """Parse flight information.

    Arguments:
        raw_flight_info {list} -- parsed from booking engine data.
        persons {int} -- total number of people to book.

    Returns:
        dict -- parsed flight information.
    """
    # TODO: write to parsed_flight_info явно
    # parsed_flight_info = {"Date": "bla-bla", etc
    parsed_flight_info = {"Date": "", "Departure": "", "Arrival": "",
                          "Flight duration": "", "From": "", "To": "",
                          "Price": "", "Additional information": ""}

    parsed_flight_info["Flight duration"] = calculate_flight_duration(
        *raw_flight_info[1:3])
    total_cost = int(raw_flight_info[-1][7:-7]) * persons
    parsed_flight_info["Price"] = f"{total_cost}.00 EUR"

    i = 0
    # TODO: add additional information handling
    for key in parsed_flight_info:
        # ! i < 6 if there is additional information
        if not parsed_flight_info[key] and i < 5:
            parsed_flight_info[key] = raw_flight_info[i]
            i += 1

    return parsed_flight_info
