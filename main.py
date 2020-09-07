import sys
import src.script as source


def main():
    """Flights_info demo."""
    source.print_flights_information(source.find_flight_info(sys.argv[1:]))


if __name__ == '__main__':
    main()
