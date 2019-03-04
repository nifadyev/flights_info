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
        # TODO: Use argparse.Namespace as expected args => get rid of try catch
        try:
            source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1"])
        except BaseException:
            self.fail("parse_arguments raised ValueError unexpectedly!")

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

    # def test_valid_persons_number(self):
    #     for persons in range(1, 10):
    #         expected_args = argparse.Namespace(dep_city="BLL",
    #                                            des_city="BOJ",
    #                                            dep_date="04.07.2019",
    #                                            persons=str(persons))
    #         with self.subTest(persons):
    #             self.assertEqual(expected_args, source.parse_arguments(
    #                 ["BLL", "BOJ", "04.07.2019", str(persons)]))

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

    def test_with_valid_args1(self):
        # TODO: try to check all available combinations
        # TODO: if it isn't too difficult
        self.assertEqual(source.calculate_flight_duration(
            "01:00", "01:01"), "00:01")


class TestCheckRoute(unittest.TestCase):
    """ """

    def setUp(self):
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

    def test_all_available_dates(self):
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

    # def test_check_date_availability_correct_cph_to_boj_one_way(self):
    # TODO: Use SetUp in this testCase (setup DATES from script.py)
    #     CPH_TO_BOJ_DATES = {"26.06.2019", "03.07.2019", "10.07.2019",
    #                         "17.07.2019", "24.07.2019", "31.07.2019",
    #                         "07.08.2019"}
    #     for date in CPH_TO_BOJ_DATES:
    #         args = argparse.Namespace(dep_city="CPH", dest_city="BOJ",
    #                                   dep_date=date,
    #                                   adults_children="1",
    #                                   return_date=None)
    #         with self.subTest(date):
    #             try:
    #                 source.check_date_availability(args, False)
    #             except ValueError:
    #                 self.fail("check_date_availability raised"
    #                           "ValueError unexpectedly!")

    # def test_check_date_availability_correct_cph_to_boj_two_way(self):
    #     CPH_TO_BOJ_DATES = {"26.06.2019", "03.07.2019", "10.07.2019",
    #                         "17.07.2019", "24.07.2019", "31.07.2019",
    #                         "07.08.2019"}
    #     BOJ_TO_CPH_DATES = {"27.06.2019", "04.07.2019", "11.07.2019",
    #                         "18.07.2019", "25.07.2019", "01.08.2019",
    #                         "08.08.2019"}
    #     for dep_date in CPH_TO_BOJ_DATES:
    #         for return_date in BOJ_TO_CPH_DATES:
    #             args = argparse.Namespace(dep_city="CPH", dest_city="BOJ",
    #                                       dep_date=dep_date,
    #                                       adults_children="1",
    #                                       return_date=return_date)
    #             with self.subTest((dep_date, return_date)):
    #                 try:
    #                     source.check_date_availability(args, True)
    #                 except ValueError:
    #                     self.fail("check_date_availability raised"
    #                               "ValueError unexpectedly!")

    # def test_check_date_availability_correct_boj_to_bll_one_way(self):
    #     BOJ_TO_BLL_DATES = {"01.07.2019", "08.07.2019", "15.07.2019",
    #                         "22.07.2019", "29.07.2019", "05.08.2019"}

    #     for date in BOJ_TO_BLL_DATES:
    #         args = argparse.Namespace(dep_city="BOJ", dest_city="BLL",
    #                                   dep_date=date,
    #                                   adults_children="1",
    #                                   return_date=None)
    #         with self.subTest(date):
    #             try:
    #                 source.check_date_availability(args, False)
    #             except ValueError:
    #                 self.fail("check_date_availability raised"
    #                           "ValueError unexpectedly!")

    # def test_check_date_availability_correct_boj_to_boj_two_way(self):
    #     CPH_TO_BOJ_DATES = {"26.06.2019", "03.07.2019", "10.07.2019",
    #                         "17.07.2019", "24.07.2019", "31.07.2019",
    #                         "07.08.2019"}
    #     BOJ_TO_CPH_DATES = {"27.06.2019", "04.07.2019", "11.07.2019",
    #                         "18.07.2019", "25.07.2019", "01.08.2019",
    #                         "08.08.2019"}
    #     for dep_date in CPH_TO_BOJ_DATES:
    #         for return_date in BOJ_TO_CPH_DATES:
    #             args = argparse.Namespace(dep_city="CPH", dest_city="BOJ",
    #                                       dep_date=dep_date,
    #                                       adults_children="1",
    #                                       return_date=return_date)
    #             with self.subTest((dep_date, return_date)):
    #                 try:
    #                     source.check_date_availability(args, True)
    #                 except ValueError:
    #                     self.fail("check_date_availability raised"
    #                               "ValueError unexpectedly!")

    # def test_check_all_unavailable_routes(self):
    #         # args = ["PDV", "BOJ", "26.06.2019", "1"]
    #     AVAILABLE_ROUTES = (("CPH", "BOJ"), ("BLL", "BOJ"), ("BOJ", "CPH"),
    #                         ("BOJ", "BLL"))
    #     CITY_CODES = ("CPH", "BLL", "PDV", "BOJ", "SOF", "VAR")

    #     for dep_city, dest_city in itertools.permutations(CITY_CODES, r=2):
    #         if (dep_city, dest_city) not in AVAILABLE_ROUTES:
    #             with self.subTest((dep_city, dest_city)):
    #                 with self.assertRaises(ValueError) as e:
    #                     source.check_route(
    #                         f"{dep_city}", f"{dest_city}")
    #                 self.assertEqual(
    #                     e.exception.args[0], f"Unavailable route")

    # def test_parse_arguments(self):
    #     """ """
    #     args = argparse.Namespace(adults_children='1', dep_city='CPH',
    #                               dep_date='26.06.2019', dest_city='BOJ',
    #                               return_date=None)
    #     input_args = ["CPH", "BOJ", "26.06.2019", "1"]

    #     self.assertEqual(source.parse_arguments(input_args), args)

    # def test_check_date(self):
    #     with self.assertRaises(ValueError) as e:
    #         source.parse_arguments(["CPH", "PDV", "26.06.2019", "1"])
    #     # e.exception.args[0] contains error message
    #     self.assertEqual(e.exception.args[0],
    #                      "Flight route CPH-PDV is unavailable")


if __name__ == '__main__':
    unittest.main()
