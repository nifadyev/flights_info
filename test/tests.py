import unittest
import argparse
import itertools
from datetime import datetime
import src.script as source


class TestValidateDate(unittest.TestCase):

    def test_too_long_date(self):
        with self.assertRaises(ValueError):
            source.validate_date("26.06.20191")

    def test_invalid_date_formats(self):
        invalid_dates = (
            "03-04-2019", "24 Aug 2019", "2019.01.24", "11.02.19", "05/11/2019"
        )

        for date in invalid_dates:
            with self.subTest(date):
                with self.assertRaises(ValueError):
                    source.validate_date(date)

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            source.validate_date("abcd")

    def test_invalid_day(self):
        with self.assertRaises(ValueError):
            source.validate_date("32.06.2019")

    def test_negative_day(self):
        with self.assertRaises(ValueError):
            source.validate_date("-12.10.2019")

    def test_invalid_month(self):
        with self.assertRaises(ValueError):
            source.validate_date("14.o8.2019")

    def test_negative_month(self):
        with self.assertRaises(ValueError):
            source.validate_date("14.-12.2019")

    def test_old_date(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.validate_date("26.01.2019")


class TestValidateCityCodes(unittest.TestCase):

    def setUp(self):
        self.valid_codes = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

    def test_valid_codes(self):
        for code in self.valid_codes:
            with self.subTest(code):
                self.assertEqual(source.validate_city_code(code), code)

    def test_invalid_type(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.validate_city_code("1234")

    def test_invalid_case(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.validate_city_code("boj")

    def test_mixed_case(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.validate_city_code("BlL")


class TestValidatePassengers(unittest.TestCase):

    def test_valid_passengers_number(self):
        args = (1, 6, 8)

        for number in args:
            with self.subTest(number):
                self.assertEqual(source.validate_passengers(number), number)

    def test_negative_passengers_number(self):
        args = (-56, -3, -1, 0)

        for number in args:
            with self.subTest(number):
                with self.assertRaises(argparse.ArgumentTypeError):
                    source.validate_passengers(number)

    def test_too_big_passengers_number(self):
        args = (9, 23, 99, 1034)

        for number in args:
            with self.subTest(number):
                with self.assertRaises(argparse.ArgumentTypeError):
                    source.validate_passengers(number)

    def test_invalid_type(self):
        with self.assertRaises(TypeError):
            source.validate_passengers("wasd")


class TestCalculateFlightDuration(unittest.TestCase):
    # ? Merge this tests into 2 big
    def test_day_flights(self):
        args = (
            ("12:40", "13:35", "00:55"), ("04:35", "12:55", "08:20"),
            ("10:20", "21:00", "10:40"), ("01:05", "23:45", "22:40")
        )

        for dep_time, arr_time, duration in args:
            with self.subTest(duration):
                self.assertEqual(
                    source.calculate_flight_duration(dep_time, arr_time),
                    duration
                )

    def test_night_flights(self):
        args = (
            ("23:30", "00:15", "00:45"), ("18:25", "00:30", "06:05"),
            ("17:40", "05:50", "12:10"), ("16:00", "15:00", "23:00")
        )

        for dep_time, arr_time, duration in args:
            with self.subTest(duration):
                self.assertEqual(
                    source.calculate_flight_duration(dep_time, arr_time),
                    duration
                )

    def test_equal_dep_time_and_arr_time(self):
        args = ("02:34", "00:12", "14:40", "23:55")

        for time in args:
            with self.subTest(time):
                self.assertEqual(
                    source.calculate_flight_duration(time, time), "00:00"
                )


class TestCheckRoute(unittest.TestCase):

    def setUp(self):
        self.city_codes = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}
        self.dates = {
            ("CPH", "BOJ"): {
                "26.06.2019", "03.07.2019", "10.07.2019", "17.07.2019",
                "24.07.2019", "31.07.2019", "07.08.2019"
            },
            ("BOJ", "CPH"): {
                "27.06.2019", "04.07.2019", "11.07.2019", "18.07.2019",
                "25.07.2019", "01.08.2019", "08.08.2019"
            },
            ("BOJ", "BLL"): {
                "01.07.2019", "08.07.2019", "15.07.2019", "22.07.2019",
                "29.07.2019", "05.08.2019"
            },
            ("BLL", "BOJ"): {
                "01.07.2019", "08.07.2019", "15.07.2019", "22.07.2019",
                "29.07.2019", "05.08.2019"
            }
        }

    def test_all_available_dates_one_way(self):
        for route in self.dates:
            for date in self.dates[route]:
                with self.subTest(date):
                    parsed_date = datetime.strptime(date, "%d.%m.%Y")
                    source.check_route(route[0], route[1], parsed_date)

    def test_unavailable_routes(self):
        flight_date = datetime.strptime("21.06.2019", "%d.%m.%Y")

        for dep_city, arr_city in itertools.permutations(self.city_codes, r=2):
            if (dep_city, arr_city) not in self.dates:
                with self.subTest((dep_city, arr_city)):
                    with self.assertRaises(KeyError):
                        source.check_route(dep_city, arr_city, flight_date)

    def test_unavailable_flight_dates(self):
        for route in self.dates:
            for date in self.dates[route]:
                with self.subTest(date):
                    parsed_date = datetime.strptime(date, "%d.%m.%Y")
                    invalid_date = parsed_date.replace(year=2018)

                    with self.assertRaises(KeyError):
                        source.check_route(route[0], route[1], invalid_date)


class TestFindFlightInfo(unittest.TestCase):

    def test_return_valid_data_one_way(self):
        args = ("BLL", "BOJ", "22.07.2019", "7")

        expected_data = {
            "Outbound": {
                "Date": "Mon, 22 Jul 19",
                "Departure": "18:45",
                "Arrival": "22:45",
                "Flight duration": "04:00",
                "From": "Billund (BLL)",
                "To": "Burgas (BOJ)",
                "Price": "1204.00 EUR",
                "Additional information": ""
            }
        }

        self.assertEqual(source.find_flight_info(args), expected_data)

    def test_return_valid_data_two_way(self):
        args = ("BOJ", "BLL", "01.07.2019", "2", "-return_date=05.08.2019")

        expected_data = {
            "Outbound": {
                "Date": "Mon, 1 Jul 19",
                "Departure": "16:00", "Arrival": "17:50",
                "Flight duration": "01:50",
                "From": "Burgas (BOJ)",
                "To": "Billund (BLL)",
                "Price": "210.00 EUR",
                "Additional information": ""
            },
            "Inbound": {
                "Date": "Mon, 5 Aug 19",
                "Departure": "18:45", "Arrival": "22:45",
                "Flight duration": "04:00",
                "From": "Billund (BLL)",
                "To": "Burgas (BOJ)",
                "Price": "210.00 EUR",
                "Additional information": ""
            }
        }

        self.assertEqual(source.find_flight_info(args), expected_data)

    def test_dep_date_in_the_past(self):
        args = ("CPH", "BOJ", "10.07.2019", "3", "-return_date=03.07.2019")

        with self.assertRaises(ValueError):
            source.find_flight_info(args)


class TestParseArguments(unittest.TestCase):
    def test_return_valid_args_one_way(self):
        args = ("BOJ", "BLL", "15.07.2019", "2")
        date = datetime.strptime("15.07.2019", "%d.%m.%Y")

        expected_args = argparse.Namespace(
            dep_city="BOJ",
            dest_city="BLL",
            dep_date=date,
            passengers=2,
            return_date=None,
            verbose=False
        )

        self.assertEqual(source.parse_arguments(args), expected_args)

    def test_return_valid_args_two_way(self):
        args = ("CPH", "BOJ", "31.07.2019", "3", "-return_date=05.08.2019")
        date = datetime.strptime("31.07.2019", "%d.%m.%Y")
        return_date = datetime.strptime("05.08.2019", "%d.%m.%Y")

        expected_args = argparse.Namespace(
            dep_city="CPH",
            dest_city="BOJ",
            dep_date=date,
            passengers=3,
            return_date=return_date,
            verbose=False
        )

        self.assertEqual(source.parse_arguments(args), expected_args)

    def test_show_help_message(self):
        with self.assertRaises(SystemExit):
            source.parse_arguments(["-h"])

    def test_invalid_dep_city(self):
        args = ("123", "BOJ", "01.07.2019", "2")

        with self.assertRaises(SystemExit):
            source.parse_arguments(args)

    def test_invalid_dest_city(self):
        args = ("CPH", "B0J", "01.07.2019", "3")

        with self.assertRaises(SystemExit):
            source.parse_arguments(args)

    def test_invalid_dep_date(self):
        args = ("CPH", "BOJ", "01.02.2019", "1")

        with self.assertRaises(SystemExit):
            source.parse_arguments(args)

    def test_invalid_passengers(self):
        args = ("BLL", "BOJ", "01.09.2019", "0")

        with self.assertRaises(SystemExit):
            source.parse_arguments(args)

    def test_invalid_return_dates(self):
        args = (
            ("BLL", "BOJ", "01.09.2019", "1", "-return-date=13.10.2019"),
            ("BLL", "BOJ", "10.06.2019", "4", "-return_date=22/08/2019"),
            ("BLL", "BOJ", "01.07.2019", "4", "-return_date=14.07.19"),
        )

        for arguments in args:
            with self.subTest(arguments):
                with self.assertRaises(SystemExit):
                    source.parse_arguments(arguments)

    def test_too_many_args(self):
        args = (
            "CPH", "B0J", "01.07.2019", "3", "-return_date=03.08.2019", "0"
        )

        with self.assertRaises(SystemExit):
            source.parse_arguments(args)

    def test_too_little_args(self):
        args = ("CPH", "B0J", "01.07.2019")

        with self.assertRaises(SystemExit):
            source.parse_arguments(args)

    def test_no_args(self):
        with self.assertRaises(SystemExit):
            source.parse_arguments(list())


class TestCreateUrlParameters(unittest.TestCase):
    def test_return_valid_parameters_one_way(self):
        date = datetime.strptime("08.07.2019", "%d.%m.%Y")
        args = argparse.Namespace(
            dep_city="BOJ",
            dest_city="BLL",
            dep_date=date,
            passengers=2,
            return_date=None
        )

        expected_args = {
            "ow": "",
            "lang": "en",
            "depdate": "08.07.2019",
            "aptcode1": "BOJ",
            "aptcode2": "BLL",
            "paxcount": 2
        }

        self.assertEqual(source.create_url_parameters(args), expected_args)

    def test_return_valid_parameters_two_way(self):
        date = datetime.strptime("18.07.2019", "%d.%m.%Y")
        return_date = datetime.strptime("31.07.2019", "%d.%m.%Y")
        args = argparse.Namespace(
            dep_city="BOJ",
            dest_city="CPH",
            dep_date=date,
            passengers=5,
            return_date=return_date
        )

        expected_args = {
            "rt": "",
            "lang": "en",
            "depdate": "18.07.2019",
            "aptcode1": "BOJ",
            "rtdate": "31.07.2019",
            "aptcode2": "CPH",
            "paxcount": 5
        }

        self.assertEqual(source.create_url_parameters(args), expected_args)


class TestWriteFlightInformation(unittest.TestCase):
    def test_return_valid_flight_info(self):
        args = (
            "Wed, 24 Jul 19", "02:45", "06:25", "Copenhagen (CPH)",
            "Burgas (BOJ)", "Price: 145.00 EUR", "", 3
        )

        expected_args = {
            "Date": "Wed, 24 Jul 19",
            "Departure": "02:45",
            "Arrival": "06:25",
            "Flight duration": "03:40",
            "From": "Copenhagen (CPH)",
            "To": "Burgas (BOJ)",
            "Price": "435.00 EUR",
            "Additional information": ""
        }

        self.assertEqual(
            source.write_flight_information(*args), expected_args
        )


if __name__ == '__main__':
    unittest.main()
