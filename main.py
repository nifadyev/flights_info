import argparse
import requests


def main():
    """ """

    argument_parser = argparse.ArgumentParser()
    # TODO: add description of IATA codes
    # TODO: create dict with impossible flights combination (also includes the same from to city)
    argument_parser.add_argument("dep_city", help="departure city IATA code", choices=[
                                 "CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"])
    argument_parser.add_argument("dest_city", help="destination city IATA code", choices=[
                                 "CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"])
    argument_parser.add_argument("dep_date", help="departure flight date")
    argument_parser.add_argument(
        "adults_children", help="Number of adults and children")  # , default="")
    argument_parser.add_argument(
        "-return_date", help="return flight date")  # , default="")
    args = argument_parser.parse_args()
    print(args)
    # TODO: do this through exception
    # TODO: handle cases when there is no return flight
    # TODO: try to create url through ternary operator
    if args.return_date:
        url = "https://apps.penguin.bg/fly/quote3.aspx?rt="\
        f"&lang=en&depdate={args.dep_date}&aptcode1={args.dep_city}"\
        f"&rtdate={args.return_date}&aptcode2={args.dest_city}"\
        f"&paxcount={args.adults_children}&infcount="
    else:
        url = "https://apps.penguin.bg/fly/quote3.aspx?ow="\
        f"&lang=en&depdate={args.dep_date}&aptcode1={args.dep_city}"\
        f"&aptcode2={args.dest_city}&paxcount={args.adults_children}&infcount="
    print(url)
        
    if requests.get(url).status_code != 200:
        # TODO: add proper comment
        raise ValueError("add proper comment")

    # TODO: add here main function call (or creating class object)
# TODO: diff between one way and return flights: ow= and rt=
# TODO: diff between one way and return flights: no rtdate and rtdate
# https://apps.penguin.bg/fly/quote3.aspx?ow=&lang=en&depdate=26.06.2019&aptcode1=CPH&aptcode2=BOJ&paxcount=1&infcount=
# https://apps.penguin.bg/fly/quote3.aspx?rt=&lang=en&depdate=26.06.2019&aptcode1=CPH&rtdate=03.07.2019&aptcode2=BOJ&paxcount=1&infcount=
if __name__ == "__main__":
    main()
