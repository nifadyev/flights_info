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
            self.fail("myFunc() raised ExceptionType unexpectedly!")

    def test_validate_date_too_input_arg(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("23.01.20191")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_too_short_arg(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("3.11.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_day(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("32.06.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_invalid_month(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("14.o8.2019")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

    def test_validate_date_too_invalid_year(self):
        with self.assertRaises(ValueError) as value_error:
            source.validate_date("31.12.2020")
            self.assertEqual(
                value_error.exception.args[0], "Invalid date format")

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
