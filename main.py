
import sys
import requests
import src.script as source


def main():
    """ """
    args = source.parse_arguments(sys.argv[1:])
    # TODO: do this through exception
    # TODO: handle cases when there is no return flight
    available_roots = {("CPH", "BOJ"), ("BLL", "BOJ"), ("BOJ", "CPH"),
                       ("BOJ", "BLL")}
    if (args.dep_city, args.dest_city) in available_roots:
        print("Alright")

    # TODO: add all available date for each root
    url = source.create_url(args)
    print(url)

    request = requests.get(url)
    if request.status_code != 200:
        # TODO: add proper comment
        raise ValueError("add proper comment")
    else:
        print("Correct request")

    source.find_flight_info(request)


if __name__ == "__main__":
    main()
