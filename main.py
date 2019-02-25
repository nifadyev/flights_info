import sys
import src.script as source


def main():
    """Demonstrate program functional."""

    source.find_flight_info(sys.argv[1:])


if __name__ == "__main__":
    main()
