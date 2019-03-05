import unittest
import argparse
import itertools
import requests
import datetime
import src.script as source

# TODO: Add docstring to each method
# TODO: use unittest.mock for parse_arguments

"""
-b (--buffer) - вывод программы при провале теста будет показан, а не скрыт,
как обычно.
-c (--catch) - Ctrl+C во время выполнения теста ожидает завершения текущего
теста и затем сообщает результаты на данный момент. Второе нажатие Ctrl+C
вызывает обычное исключение KeyboardInterrupt.
-f (--failfast) - выход после первого же неудачного теста.
--locals (начиная с Python 3.5) - показывать локальные переменные для
провалившихся тестов.
"""


class TestProgram(unittest.TestCase):
    """ """

    def test_no_errors_with_correct_args_one_way(self):
        # expected_args = argparse.Namespace(dep_city="CPH",
        #                                    des_city="BOJ",
        #                                    dep_date="26.06.2019",
        #                                    persons="1")
        # TODO: Use argparse.Namespace as expected args => get rid of try catch
        try:
            source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1"])
        except BaseException:
            self.fail("parse_arguments raised ValueError unexpectedly!")

        # self.assertEqual(source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1"]),
        #                  expected_args)

    def test_no_errors_with_correct_args_two_way(self):
        try:
            source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1",
                                    "-return_date=04.07.2019"])
        except BaseException:
            self.fail("parse_arguments raised ValueError unexpectedly!")


class TestValidateDate(unittest.TestCase):
    """ """

    def test_too_long_date(self):
        with self.assertRaises(ValueError):
            source.validate_date("26.06.20191")

    def test_invalid_date_format1(self):
        with self.assertRaises(ValueError):
            source.validate_date("03-04-2019")

    def test_invalid_date_format2(self):
        with self.assertRaises(ValueError):
            source.validate_date("24 Aug 2019")

    def test_invalid_date_format3(self):
        with self.assertRaises(ValueError):
            source.validate_date("2019.01.24")

    def test_invalid_date_format4(self):
        with self.assertRaises(ValueError):
            source.validate_date("11.02.19")

    def test_invalid_date_format5(self):
        with self.assertRaises(ValueError):
            source.validate_date("05/11/2019")

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
        with self.assertRaises(ValueError):
            source.validate_date("26.01.2019")


class TestValidateCityCodes(unittest.TestCase):
    """ """

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


class TestValidatePersons(unittest.TestCase):
    """ """

    def test_valid_persons_number(self):
        for persons in range(1, 10):
            with self.subTest(persons):
                self.assertEqual(source.validate_persons(persons), persons)

    def test_negative_persons_number(self):
        for persons in range(-100, 1):
            with self.subTest(persons):
                with self.assertRaises(argparse.ArgumentTypeError):
                    source.validate_persons(persons)

    def test_too_big_persons_number(self):
        for persons in range(10, 100):
            with self.subTest(persons):
                with self.assertRaises(argparse.ArgumentTypeError):
                    source.validate_persons(persons)

    def test_invalid_type1(self):
        with self.assertRaises(TypeError):
            source.validate_persons("g")

    def test_invalid_type2(self):
        with self.assertRaises(TypeError):
            source.validate_persons("wasd")


class TestCalculateFlightDuration(unittest.TestCase):
    """ """
    # TODO: try with subTest

    def test_duration_less_than_1(self):
        self.assertEqual(source.calculate_flight_duration(
            "12:40", "13:35"), "00:55")

    def test_duration_less_than_10(self):
        self.assertEqual(source.calculate_flight_duration(
            "04:35", "12:55"), "08:20")

    def test_duration_more_than_10(self):
        self.assertEqual(source.calculate_flight_duration(
            "10:20", "21:00"), "10:40")

    def test_duration_more_than_20(self):
        self.assertEqual(source.calculate_flight_duration(
            "01:05", "23:45"), "22:40")

    def test_night_flight_duration_less_than_1(self):
        self.assertEqual(source.calculate_flight_duration(
            "23:30", "00:15"), "00:45")

    def test_night_flight_duration_less_than_10(self):
        self.assertEqual(source.calculate_flight_duration(
            "18:25", "00:30"), "06:05")

    def test_night_flight_duration_more_than_10(self):
        self.assertEqual(source.calculate_flight_duration(
            "17:40", "05:50"), "12:10")

    def test_night_flight_duration_more_than_20(self):
        self.assertEqual(source.calculate_flight_duration(
            "16:00", "15:00"), "23:00")

    def test_equal_dep_time_and_arr_time(self):
        for hours in range(24):
            for minutes in range(60):
                str_hours = str(hours) if hours >= 10 else f"0{hours}"

                with self.subTest(hours):
                    time = ":".join([str_hours, str(minutes)])
                    self.assertEqual(
                        source.calculate_flight_duration(time, time), "00:00")


class TestCheckRoute(unittest.TestCase):
    """ """

    def setUp(self):
        self.city_codes = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}
        self.dates = {
            ("CPH", "BOJ"): {"26.06.2019", "03.07.2019", "10.07.2019",
                             "17.07.2019", "24.07.2019", "31.07.2019",
                             "07.08.2019"},
            ("BOJ", "CPH"): {"27.06.2019", "04.07.2019", "11.07.2019",
                             "18.07.2019", "25.07.2019", "01.08.2019",
                             "08.08.2019"},
            ("BOJ", "BLL"): {"01.07.2019", "08.07.2019", "15.07.2019",
                             "22.07.2019", "29.07.2019", "05.08.2019"},
            ("BLL", "BOJ"): {"01.07.2019", "08.07.2019", "15.07.2019",
                             "22.07.2019", "29.07.2019", "05.08.2019"}}

    def test_all_available_dates_one_way(self):
        for route in self.dates:
            for date in self.dates[route]:
                with self.subTest(date):
                    try:
                        parsed_date = datetime.datetime.strptime(date,
                                                                 "%d.%m.%Y")
                        source.check_route(route[0], route[1],
                                           parsed_date, None)
                    except BaseException:
                        self.fail("check_route raised error unexpectedly!")

    def test_dep_date_in_the_past1(self):
        dep_date = datetime.datetime.strptime("21.07.2019", "%d.%m.%Y")
        return_date = datetime.datetime.strptime("20.07.2019", "%d.%m.%Y")

        with self.assertRaises(ValueError):
            source.check_route("BLL", "BOJ", dep_date, return_date)

    def test_dep_date_in_the_past2(self):
        dep_date = datetime.datetime.strptime("23.09.2019", "%d.%m.%Y")
        return_date = datetime.datetime.strptime("01.04.2019", "%d.%m.%Y")

        with self.assertRaises(ValueError):
            source.check_route("CPH", "BOJ", dep_date, return_date)

    def test_dep_date_in_the_past3(self):
        dep_date = datetime.datetime.strptime("14.08.2020", "%d.%m.%Y")
        return_date = datetime.datetime.strptime("14.08.2019", "%d.%m.%Y")
        with self.assertRaises(ValueError):
            source.check_route("BOJ", "BLL", dep_date, return_date)

    def test_unavailable_routes_outbound(self):
        dep_date = datetime.datetime.strptime("21.06.2019", "%d.%m.%Y")

        for dep_city, dest_city in itertools.permutations(self.city_codes, r=2):
            if (dep_city, dest_city) not in self.dates:
                with self.subTest((dep_city, dest_city)):
                    with self.assertRaises(KeyError):
                        source.check_route(
                            dep_city, dest_city, dep_date, None)

    def test_unavailable_routes_inbound(self):
        dep_date = datetime.datetime.strptime("01.07.2019", "%d.%m.%Y")
        return_date = datetime.datetime.strptime("05.09.2019", "%d.%m.%Y")

        for dep_city, dest_city in itertools.permutations(self.city_codes, r = 2):
            if (dest_city, dep_city) not in self.dates:
                with self.subTest((dep_city, dest_city)):
                    with self.assertRaises(KeyError):
                        source.check_route(
                            dest_city, dep_city, dep_date, return_date)

    def test_unavailable_departure_dates(self):
        for route in self.dates:
            for date in self.dates[route]:
                with self.subTest(date):
                    parsed_date=datetime.datetime.strptime(date,
                                                             "%d.%m.%Y")
                    invalid_date=datetime.datetime(year = parsed_date.year-1,
                                                     month=parsed_date.month,
                                                     day=parsed_date.day)
                    with self.assertRaises(KeyError):
                        source.check_route(route[0], route[1],
                                           invalid_date, None)

    def test_unavailable_return_dates(self):
        for route in self.dates:
            for date in self.dates[route]:
                with self.subTest(date):
                    parsed_date = datetime.datetime.strptime(date,
                                                             "%d.%m.%Y")
                    invalid_date = datetime.datetime(year=parsed_date.year+1,
                                                     month=parsed_date.month,
                                                     day=parsed_date.day)
                    with self.assertRaises(KeyError):
                        source.check_route(route[0], route[1],
                                           parsed_date, invalid_date)


if __name__ == '__main__':
    unittest.main()
