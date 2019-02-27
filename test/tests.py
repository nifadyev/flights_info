import unittest
import requests
import src.script as source
import argparse
import itertools


class TestProgram(unittest.TestCase):
    """ """

    def test_no_errors_with_correct_args(self):
        try:
            source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1"])
        except ValueError:
            self.fail("parse_arguments raised ValueError unexpectedly!")

    def test_validate_date_too_long_date(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("23.01.20191")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_too_short_date(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("3.11.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_date_format(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("03-04-2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_date_structure(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("2019.01.24")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_type(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("abcd")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_day(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("32.06.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_negative_day(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("-12.10.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_month(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("14.o8.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_negative_month(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("14.-12.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_too_invalid_year(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("31.12.2020")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_old_date(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("25.02.2019")
            self.assertEqual(
                value_error.exception.args[0], "Old date")

    def test_check_date_availability_correct_cph_to_boj_one_way(self):

        CPH_TO_BOJ_DATES = {"26.06.2019", "03.07.2019", "10.07.2019",
                            "17.07.2019", "24.07.2019", "31.07.2019",
                            "07.08.2019"}
        for date in CPH_TO_BOJ_DATES:
            args = argparse.Namespace(dep_city="CPH", dest_city="BOJ",
                                      dep_date=date,
                                      adults_children="1",
                                      return_date=None)
            with self.subTest(date):
                try:
                    source.check_date_availability(args, False)
                except ValueError:
                    self.fail("check_date_availability raised"
                              "ValueError unexpectedly!")

    def test_check_date_availability_correct_cph_to_boj_two_way(self):
        CPH_TO_BOJ_DATES = {"26.06.2019", "03.07.2019", "10.07.2019",
                            "17.07.2019", "24.07.2019", "31.07.2019",
                            "07.08.2019"}
        BOJ_TO_CPH_DATES = {"27.06.2019", "04.07.2019", "11.07.2019",
                            "18.07.2019", "25.07.2019", "01.08.2019",
                            "08.08.2019"}
        for dep_date in CPH_TO_BOJ_DATES:
            for return_date in BOJ_TO_CPH_DATES:
                args = argparse.Namespace(dep_city="CPH", dest_city="BOJ",
                                          dep_date=dep_date,
                                          adults_children="1",
                                          return_date=return_date)
                with self.subTest((dep_date, return_date)):
                    try:
                        source.check_date_availability(args, True)
                    except ValueError:
                        self.fail("check_date_availability raised"
                                  "ValueError unexpectedly!")

    def test_check_date_availability_correct_boj_to_bll_one_way(self):
        BOJ_TO_BLL_DATES = {"01.07.2019", "08.07.2019", "15.07.2019",
                            "22.07.2019", "29.07.2019", "05.08.2019"}

        for date in BOJ_TO_BLL_DATES:
            args = argparse.Namespace(dep_city="BOJ", dest_city="BLL",
                                      dep_date=date,
                                      adults_children="1",
                                      return_date=None)
            with self.subTest(date):
                try:
                    source.check_date_availability(args, False)
                except ValueError:
                    self.fail("check_date_availability raised"
                              "ValueError unexpectedly!")

    def test_check_date_availability_correct_boj_to_boj_two_way(self):
        CPH_TO_BOJ_DATES = {"26.06.2019", "03.07.2019", "10.07.2019",
                            "17.07.2019", "24.07.2019", "31.07.2019",
                            "07.08.2019"}
        BOJ_TO_CPH_DATES = {"27.06.2019", "04.07.2019", "11.07.2019",
                            "18.07.2019", "25.07.2019", "01.08.2019",
                            "08.08.2019"}
        for dep_date in CPH_TO_BOJ_DATES:
            for return_date in BOJ_TO_CPH_DATES:
                args = argparse.Namespace(dep_city="CPH", dest_city="BOJ",
                                          dep_date=dep_date,
                                          adults_children="1",
                                          return_date=return_date)
                with self.subTest((dep_date, return_date)):
                    try:
                        source.check_date_availability(args, True)
                    except ValueError:
                        self.fail("check_date_availability raised"
                                  "ValueError unexpectedly!")

    def test_check_all_unavailable_routes(self):
            # args = ["PDV", "BOJ", "26.06.2019", "1"]
        AVAILABLE_ROUTES = (("CPH", "BOJ"), ("BLL", "BOJ"), ("BOJ", "CPH"),
                            ("BOJ", "BLL"))
        CITY_CODES = ("CPH", "BLL", "PDV", "BOJ", "SOF", "VAR")

        for dep_city, dest_city in itertools.permutations(CITY_CODES, r=2):
            if (dep_city, dest_city) not in AVAILABLE_ROUTES:
                with self.subTest((dep_city, dest_city)):
                    with self.assertRaises(ValueError) as e:
                        source.check_route(
                            f"{dep_city}", f"{dest_city}")
                    self.assertEqual(
                        e.exception.args[0], f"Unavailable route")

    def test_parse_arguments(self):
        """ """
        args = argparse.Namespace(adults_children='1', dep_city='CPH',
                                  dep_date='26.06.2019', dest_city='BOJ',
                                  return_date=None)
        input_args = ["CPH", "BOJ", "26.06.2019", "1"]

        self.assertEqual(source.parse_arguments(input_args), args)

    # def test_check_date(self):
    #     with self.assertRaises(ValueError) as e:
    #         source.parse_arguments(["CPH", "PDV", "26.06.2019", "1"])

    #     # e.exception.args[0] contains error message
    #     self.assertEqual(e.exception.args[0],
    #                      "Flight route CPH-PDV is unavailable")


if __name__ == '__main__':
    unittest.main()
