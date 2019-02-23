
import sys
import src.script as source


def main():
    """ """
    args = source.parse_arguments(sys.argv[1:])
    # result = None
    # while result is None:
    #     try:
    #         # connect
    #         result = get_data(...)
    #     except:
    #         pass
    # # other code that uses result but is not involved in getting it
    # TODO: do this through exception

    source.find_flight_info(args)


if __name__ == "__main__":
    main()
