import unittest
import argparse
import itertools
import requests
import src.script as source

# TODO: Add docstring to each method

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


class TestParseArgumentsDepartureDate(unittest.TestCase):
    """ """

    def test_too_long_date(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["CPH", "BOJ", "26.06.20191", "1"])

    def test_invalid_date_format1(self):
        # with self.assertRaises(argparse.ArgumentTypeError) as exc:
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "03-04-2019", "6"])
            # self.assertEqual(exc.exception.args[0],
            # "argparse.ArgumentTypeError: argument dep_date:"
            # "invalid validate_date value: '26.13.2019'")

    def test_invalid_date_format2(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "24 Aug 2019", "6"])

    def test_invalid_date_format3(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "2019.01.24", "6"])

    def test_invalid_date_format4(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "11.02.19", "6"])

    def test_invalid_date_format5(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "05/11/2019", "6"])

    def test_invalid_type(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "abcd", "4"])

    def test_invalid_day(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "BOJ", "32.06.2019", "3"])

    def test_negative_day(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "-12.10.2019", "6"])

    def test_invalid_month(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "14.o8.2019", "1"])

    def test_negative_month(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "14.-12.2019", "2"])

    def test_old_date(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "26.01.2019", "4"])


class TestParseArgumentsReturnDate(unittest.TestCase):
    """ """

    def test_too_long_date(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "BOJ", "12.04.2019", "4",
                                    "-return_date=26.06.20202"])

    def test_invalid_date_format1(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "CPH", "29.07.2019", "3",
                                    "-return_date=03-04-2019"])

    def test_invalid_date_format2(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "01.10.2019", "6",
                                    "-return_date=24 Aug 2019"])

    def test_invalid_date_format3(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "CPH", "09.09.2019", "9",
                                    "-return_date=2019.01.24"])

    def test_invalid_date_format4(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "19.04.2019", "4",
                                    "-return_date=11.02.19"])

    def test_invalid_date_format5(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "15.12.2019", "4",
                                    "-return_date=11/02/19"])

    def test_invalid_type(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "BOJ", "12.08.2019", "4",
                                    "-return_date=qwerty"])

    def test_invalid_day(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "BOJ", "02.05.2019", "3",
                                    "-return_date=31.04.2019"])

    def test_negative_day(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "12.12.2019", "6",
                                    "-return_date=-22.08.2019"])

    def test_invalid_month(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "14.08.2019", "3",
                                    "-return_date=23.1o.2019"])

    def test_negative_month(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BLL", "CPH", "11.09.2019", "2",
                                    "-return_date=08.-10.2019"])

    def test_old_date(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            source.parse_arguments(["BOJ", "BLL", "26.08.2019", "9",
                                    "-return_date=01.03.2019"])

# class TestParseArgumentsDepartureCity(unittest.TestCase):
#     """ """
#     def SetUp(self):
#         VALID_CITY_CODES = {"CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"}

        # TODO: Use argparse.Namespace as expected args => get rid of try catch
        # try:
        #     source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1"])
        # except BaseException:
        #     self.fail("parse_arguments raised ValueError unexpectedly!")
    # def test_invalid_case(self):

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
