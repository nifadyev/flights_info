import unittest
import requests
import src.script as source
import argparse
# import main
import itertools


class TestProgram(unittest.TestCase):
    """ """
    # def test_run_main(self):

    def test_parse_arguments(self):
        """ """
        args = argparse.Namespace(adults_children='1', dep_city='CPH',
                                  dep_date='26.06.2019', dest_city='BOJ',
                                  return_date=None)
        input_args = ["CPH", "BOJ", "26.06.2019", "1"]

        self.assertEqual(source.parse_arguments(input_args), args)

    def test_check_date(self):
        with self.assertRaises(ValueError) as e:
            source.parse_arguments(["CPH", "PDV", "26.06.2019", "1"])

        # e.exception.args[0] contains error message
        self.assertEqual(e.exception.args[0], "Flight route CPH-PDV is unavailable")

    def test_run_test(self):
        try:
            source.parse_arguments(["CPH", "BOJ", "26.06.2019", "1"])
        except ValueError:
            self.fail("myFunc() raised ExceptionType unexpectedly!")


    # def test_check_root(self):
    #     """ """
    #     args = argparse.Namespace(adults_children='1', dep_city='CPH',
    #                               dep_date='26.06.2019', dest_city='BOJ',
    #                               return_date=None)
    #     input_args = ["CPH", "BOJ", "26.06.2019", "1"]
    #     city_codes = ["CPH", "BLL", "PDV", "BOJ", "SOF", "VAR"]
    #     all_roots = itertools.permutations(city_codes, r=2)
    #     # print(all_roots)
    #     count = 0
    #     for i, j in itertools.permutations(city_codes, r=2):
    #         input_args[0] = i
    #         input_args[1] = j
    #         with self.subTest(i=count):
    #             self.assertEqual(source.parse_arguments(input_args), args)
    #         count += 1
if __name__ == '__main__':
    unittest.main()
