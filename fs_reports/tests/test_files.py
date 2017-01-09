"""
Unit tests on the file handling

"""
from unittest import TestCase
from pathlib import Path

import datetime

from fs_reports import files as files

month_labels = "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"


def dummy_locations():
    """
    folder name for dummy locations

    :return path: path to dummy locations (have to add in filename)
    """
    p = Path.cwd()
    return p.joinpath('tests/dummy_files')


class Files(TestCase):
    """
    Test the ward handling

    """
    @classmethod
    def setUp(cls):
        """
        Setup environment for the Ward tests
        :return:
        """

    def test_current_directory(self):
        """
        get current directory

        :return:
        """
        report_current = files.build_path_to_report_directory()
        self.assertTrue(report_current is not None)
        self.assertTrue(report_current.exists())
        self.assertTrue(report_current.is_dir())

    def test_clear_current(self):
        """
        clear out the current directory contents

        :return:
        """
        file_list = files.clear_report_directory()
        self.assertTrue(len(file_list) == 0)

    def test_filename(self):
        """
        build the file name

        :return:
        """
        current_month = datetime.datetime(2015, 12, 1)
        fn = files.build_ward_month_filename('Aloha I', current_month)
        test_path = Path(fn)
        self.assertTrue(test_path.name == 'Aloha I_201512.pdf')

    def test_table_name(self):
        """
        build table name

        :return:
        """
        fn = files.build_table_name()
        self.assertTrue(fn is not None)
        test_path = Path(fn)
        self.assertTrue(test_path.name == 'table.csv')

    def test_stake_filename(self):
        """
        stake file name

        :return:
        """
        d1 = datetime.datetime(2015, 12, 1)
        fn = files.build_stake_month_name(d1)
        self.assertTrue(fn is not None)
        self.assertTrue(str(fn) == 'Stake_201512.pdf')

    def test_stake_path(self):
        """
        full path test

        :return:
        """
        d1 = datetime.datetime(2015, 12, 1)
        fn = files.build_stake_report_name(d1)
        self.assertTrue(fn is not None)
        test_path = Path(fn)
        self.assertTrue(test_path.name == 'Stake_201512.pdf')


class DownloadFiles(TestCase):
    """
    testing of the download file handling

    """
    @classmethod
    def setUp(cls):
        """
        Setup environment for the Ward tests
        :return:
        """

    def test_download_directory(self):
        """
        find the downloaded file

        :return:
        """
        fn = files.locate_downloaded_lsr()
        full_path = fn.parent
        self.assertTrue(full_path.parent == Path.home())
        self.assertTrue(full_path.stem == 'Downloads')
        self.assertTrue(fn.name == 'LocationStatisticsReport.csv')

    def test_data_directory(self):
        """
        test directory to move files to

        :return:
        """
        fn = files.data_download_directory()
        self.assertTrue(fn.stem == 'downloads')

    def test_lsr_name(self):
        """
        test for lsr name

        :return:
        """
        d1 = datetime.datetime(2016, 1, 1)
        fn = files.build_lsr_name(d1)
        self.assertTrue(fn == 'lsr_201601.csv')

    def test_slc_move(self):
        """
        move the slc download to our directory

        :return:
        """
        # TODO rewrite to make this non-destructive of the real files

        # self.setup_lsr_files()
        # gc.current_month = datetime.datetime(2016, 1, 1)
        # files.move_slc_download()
        # destination = files.data_download_directory()
        # destination = destination.joinpath(files.build_lsr_name(gc.current_month))
        # self.assertTrue(destination.exists())
        pass
