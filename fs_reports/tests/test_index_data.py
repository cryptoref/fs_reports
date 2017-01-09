"""
Unit tests on the csv file

"""
import unittest
from pathlib import Path
import datetime

import fs_reports.index_data as iv


def dummy_locations():
    """
    folder name for dummy locations

    :return path: path to dummy locations (have to add in filename)
    """
    p = Path.cwd()
    return p.joinpath('tests/dummy_files')


class CreateTable(unittest.TestCase):
    """
    Test on class creation


    """

    @classmethod
    def setUp(self):
        """
        Setup environment for the Ward tests

        :return:
        """
        unittest.TestCase.setUp(self)
        self.test_table = iv.IndexerValues()

    def test_create_class(self):
        """ create the class """
        current_table = iv.IndexerValues()
        self.assertTrue(current_table is not None)

        # check the date format
        self.assertTrue(current_table.date_format == "%Y-%m-%d")

    def test_add_month(self):
        """add month testing"""
        test_date = datetime.datetime(2012, 12, 1)
        self.assertTrue(self.test_table.add_month(test_date) == datetime.datetime(2013, 1, 1))

        test_date = datetime.datetime(2016, 1, 1)
        self.assertTrue(self.test_table.add_month(test_date) == datetime.datetime(2016, 2, 1))

        test_date = datetime.datetime(2016, 2, 1)
        self.assertTrue(self.test_table.add_month(test_date) == datetime.datetime(2016, 3, 1))

    def test_load_file(self):
        """ load csv file """
        fn = dummy_locations()
        fn = fn.joinpath('dummy_table_201512.csv')
        current_table = self.test_table.read_table_name(fn)
        self.assertTrue(current_table is not None)

        # test that all of the attributes filled out
        self.assertTrue(self.test_table.ward_list is not None)
        self.assertTrue(self.test_table.list_of_months is not None)
        self.assertTrue(self.test_table.sorted_wards is not None)

        # check for the right number of records
        self.assertTrue(len(current_table == 1327))
        self.assertTrue(len(self.test_table.ward_list) == 8)
        self.assertTrue(len(self.test_table.list_of_months) == 36)

        self.assertTrue(self.test_table.first_month == datetime.datetime(2013, 1, 1))
        self.assertTrue(self.test_table.last_month == datetime.datetime(2015, 12, 1))
        self.assertTrue(self.test_table.next_month == datetime.datetime(2016, 1, 1))
        self.assertTrue(self.test_table.year_count == 3)

        self.assertTrue(self.test_table.sorted_wards[0] == 'Hazeldale')

        self.assertTrue(len(self.test_table.current_table.Name.unique()) == 277)

    def test_ini(self):
        """ test ini loading """

        _fn = 'tests/test.ini'

        user = 'User1'
        stake_name = 'Kolob Stake'
        to_email = 'cryptoref@gmail.com'

        self.test_table.read_ini_filename(_fn)
        self.assertTrue(user == self.test_table.username)
        self.assertTrue(stake_name == self.test_table.stake_name)
        self.assertTrue(to_email == self.test_table.to_email)
        self.assertTrue(to_email == self.test_table.from_email)


class GetMonth(unittest.TestCase):
    """
    Load in the month

    """

    @classmethod
    def setUp(self):
        """
        Setup environment for the Ward tests

        :return:
        """
        unittest.TestCase.setUp(self)
        fn = dummy_locations()
        fn = fn.joinpath('dummy_table_201512.csv')
        self.index_class = iv.IndexerValues()
        self.index_class.read_table_name(fn)

    def test_load(self):
        """

        :return:

        """
        fn = dummy_locations()
        fn = fn.joinpath('dummy_lsr_201601_fixed.csv')
        month_to_load = datetime.datetime(2016, 1, 1)
        self.index_class.load_this_month_file(fn, month_to_load)

        self.assertTrue(self.index_class.month_data is not None)

        # test that all of the attributes filled out
        self.assertTrue(self.index_class.ward_list is not None)
        self.assertTrue(self.index_class.list_of_months is not None)
        self.assertTrue(self.index_class.sorted_wards is not None)

        # check for the right number of records
        self.assertTrue(len(self.index_class.month_data == 34))
        self.assertTrue(self.index_class.bad_wards is None)
        self.assertTrue(len(self.index_class.current_table == 1327))

        # now do the merge after we know we have the right split
        self.index_class.merge_month_to_table()
        self.assertTrue(self.index_class.month_data is None)

        self.assertTrue(len(self.index_class.current_table == 1361))
        self.assertTrue(len(self.index_class.ward_list) == 8)
        self.assertTrue(len(self.index_class.list_of_months) == 37)

        self.assertTrue(self.index_class.first_month == datetime.datetime(2013, 1, 1))
        self.assertTrue(self.index_class.last_month == datetime.datetime(2016, 1, 1))
        self.assertTrue(self.index_class.year_count == 4)

        self.assertTrue(self.index_class.sorted_wards[0] == 'Hazeldale')

        self.assertTrue(len(self.index_class.current_table.Name.unique()) == 281)

        # do it again and it should fail
        df = self.index_class.load_this_month_file(fn, month_to_load)
        self.assertTrue(df is None)


class GetBadNames(unittest.TestCase):
    """
    Load in month that has bad ward names

    Need to get the list of users who match the bad wards

    """

    @classmethod
    def setUp(self):
        """
        Setup environment for the Ward tests

        :return:
        """
        unittest.TestCase.setUp(self)
        fn = dummy_locations()
        fn = fn.joinpath('dummy_table_201512.csv')
        self.test_table = iv.IndexerValues()
        self.test_table.read_table_name(fn)

    def test_bad_names(self):
        """

        :return:

        """
        fn = dummy_locations()
        fn = fn.joinpath('dummy_lsr_201601.csv')
        month_to_load = datetime.datetime(2016, 1, 1)
        current_table = self.test_table.load_this_month_file(fn, month_to_load)

        self.assertTrue(current_table is not None)


class DataframeSlicing(unittest.TestCase):
    """
    Test slices through the dataframe

    """

    @classmethod
    def setUp(self):
        """
        Setup environment for the Ward tests

        :return:
        """
        unittest.TestCase.setUp(self)
        fn = dummy_locations()
        fn = fn.joinpath('dummy_table_201512.csv')
        self.my_data = iv.IndexerValues()
        self.my_data.read_table_name(fn)

    def test_counts_by_date(self):
        """
        Get counts by date

        :return:
        """
        counts = [15, 41, 45, 46, 42, 38, 36, 34, 26, 24, 29, 27,
                  27, 33, 31, 39, 32, 39, 47, 36, 32, 28, 27, 25,
                  37, 53, 42, 41, 47, 40, 36, 81, 44, 41, 35, 31]

        df_sum = self.my_data.counts_by_date(self.my_data.current_table, ['Indexed'])
        self.assertTrue(df_sum is not None)
        self.assertTrue(len(df_sum) == 36)

        for index_row, value in enumerate(df_sum):
            self.assertTrue(value == counts[index_row])

    def test_ward_slices(self):
        """slice off a ward and then check the sums"""

        # ward slice
        df = self.my_data.ward_slice('Aloha I')

        # date sums
        df_value = self.my_data.sums_by_date(df, 'Indexed')
        self.assertTrue(df_value[0] == 1874)
        self.assertTrue(df_value[35] == 814)
        self.assertTrue(len(df_value) == 36)

        df_count = self.my_data.counts_by_date(df, 'Indexed')
        self.assertTrue(df_count[0] == 4)
        self.assertTrue(df_count[35] == 7)
        self.assertTrue(len(df_count) == 36)

        # redo tests using ward that has missing sums
        df = self.my_data.ward_slice('Cooper Mtn')
        df_value = self.my_data.sums_by_date(df, 'Indexed')
        self.assertTrue(df_value[0] == 0)
        self.assertTrue(df_value[35] == 1715)
        self.assertTrue(len(df_value) == 36)

    def test_ward_sums(self):
        """
        The pie month and year dataframe

        :return:
        """
        # counts for all 3 years and december 2015 only
        counts = [['Hazeldale', 110663], ['Murrayhill', 71444], ['Reedville', 42886], ['Aloha II', 22145],
                  ['Cooper Mtn', 10423], ['Aloha I', 8084], ['No Ward', 6268], ['Farmington', 832]]
        count_month = [['Hazeldale', 3113], ['Murrayhill', 8447], ['Reedville', 1373], ['Aloha II', 166],
                       ['Cooper Mtn', 1715], ['Aloha I', 814]]

        # do year first as that will set the order for doing the legend and month
        stake_year = self.my_data.ward_year_sum()
        for index_row, row in enumerate(stake_year.iterrows()):
            self.assertTrue(row[0] == counts[index_row][0])
            self.assertTrue(row[1][0] == counts[index_row][1])

        stake_month = self.my_data.ward_month_sum(stake_year)
        for index_row, row in enumerate(stake_month.iterrows()):
            self.assertTrue(row[0] == count_month[index_row][0])
            self.assertTrue(row[1][0] == count_month[index_row][1])

    def test_ward_count(self):
        """
        test the ward count

        """
        fixed_counts = [[10593,  9192,  1641,  5635,  4126,  2597,  1560,  1124,   352,  1098,  4707,   404,
                         2619,  3525,  1611,  3060,  3320,  2552,  2108,  2166,  4373,  6945, 13368, 18686,
                         19920, 16995, 11418, 10973,  7643,  5192,  5791,  9907,  9231,  5146,  5334,  3113],
                        [3859,  2839,  3656, 13799,  5497,  4856,  2115,  7369,  9029,  6828, 21427,  4858,
                         4303,  4037,  2756,  3939,  4104,  3444,  3498,  2590,  2987,  3158,  3448,  3033,
                         3422,  3688,  2188,  1992,  4197,  2837,  5880,  9782, 10285,  9142,  9584,  8447]]

        count_array = self.my_data.ward_count_arrays('Indexed')
        for index_row, row in enumerate(fixed_counts):
            for index_count, value in enumerate(row):
                self.assertTrue(value == fixed_counts[index_row][index_count])

    def test_individual_list(self):
        """ get individual list """
        individuals = self.my_data.individual_list(self.my_data.current_table, 2, 500, "Indexed")
        self.assertTrue(individuals is not None)
        self.assertTrue(len(individuals) == 42)
        sums = individuals.sum()
        self.assertTrue(sums['Indexed'] == 35941)

        individuals = self.my_data.individual_list(self.my_data.current_table, 1, 200, 'Indexed')
        self.assertTrue(individuals is not None)
        self.assertTrue(len(individuals) == 30)
        sums = individuals.sum()
        self.assertTrue(sums['Indexed'] == 15628)

        individuals = self.my_data.individual_list(self.my_data.current_table, 1, 1, 'Indexed')
        self.assertTrue(individuals is not None)
        self.assertTrue(len(individuals) == 1)
        sums = individuals.sum()
        self.assertTrue(sums['Indexed'] == 15628)

        individuals = self.my_data.individual_list(self.my_data.current_table, 1, 20, 'Indexed')
        self.assertTrue(individuals is not None)
        self.assertTrue(len(individuals) == 20)
        sums = individuals.sum()
        self.assertTrue(sums['Indexed'] == 15628)

        individuals = self.my_data.individual_list(self.my_data.current_table, 1, 200, "Arbitrated")
        self.assertTrue(individuals is not None)
        self.assertTrue(len(individuals) == 4)
        sums = individuals.sum()
        self.assertTrue(sums['Arbitrated'] == 6401)

        individuals = self.my_data.individual_list(self.my_data.current_table, 1, 20, "Arbitrated")
        self.assertTrue(individuals is not None)
        self.assertTrue(len(individuals) == 4)
        sums = individuals.sum()
        self.assertTrue(sums['Arbitrated'] == 6401)