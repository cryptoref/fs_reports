"""
Handle the files and directories for the reports

"""

# system imports
import os
import shutil
from pathlib import Path
# package imports
# module imports


def build_path_to_report_directory():
    """
    Check for report directory that will hold stake and ward reports, if not present build them

    :return Path: path to current report directory
    """
    current = Path.cwd()
    parent = current.parent
    report_current = parent.joinpath('reports/current')
    return report_current


def clear_report_directory():
    """
    remove any files in the current directory (makes sending email easier later

    :return list: return the empty list (for unit testing)
    """
    report_current = build_path_to_report_directory()
    file_generator = report_current.glob('*.*')
    try:
        for idx, file_name in enumerate(file_generator):
            os.remove(str(file_name))
    except PermissionError as e:
        print(e)
    file_generator = report_current.glob('*.*')
    return [x for x in file_generator]


def build_ward_month_filename(ward, current_month):
    """
    Build the ward file name based on current month

    :param ward: string of ward to use
    :param current_month: month for the report
    :return string: filename with full path
    """
    this_month = current_month.strftime('_%Y%m')
    fn = (ward + this_month + '.pdf')
    report_current = build_path_to_report_directory()
    report_current = report_current.joinpath(fn)
    return str(report_current)


def locate_downloaded_lsr():
    """
    find the downloaded month information

    :return Path: path to downloaded file
    """
    home = Path.home()
    download_directory = home.joinpath("Downloads")
    download_directory = download_directory.joinpath('LocationStatisticsReport.csv')
    return download_directory


def data_download_directory():
    """
    Directory of where to put downloaded and renamed files

    :return:
    """
    parent = Path.cwd().parent
    data_downloads = parent.joinpath('data/downloads')
    return data_downloads


def build_data_directory():
    """
    build directory for where data is kept

    :return:
    """
    parent = Path.cwd().parent
    data_downloads = parent.joinpath('data')
    return data_downloads


def build_table_name():
    """
    build the table name

    :return string: filename with complete path
    """
    fn = build_data_directory()
    fn = fn.joinpath('table.csv')
    return str(fn)


def build_lsr_name(current_date):
    """
    build lsr file name from current month

    :param current_date: datetime to build from
    :return:
    """
    this_month = current_date.strftime('%Y%m')
    fn = ('lsr_' + this_month + '.csv')
    return fn


def build_lsr_path(current_date):
    """
    build full path to lsr

    :param current_date: date for lsr name
    :return string: full path string
    """
    fn = data_download_directory()
    fn = fn.joinpath(build_lsr_name(current_date))
    return str(fn)


def move_and_rename(source, destination, remove_old):
    """
    move from the download directory to working directory and rename

    :param source: Path to source file
    :param destination: Path name for destination
    :param remove_old: boolean to remove duplicate destination
    :return boolean:
    """
    if remove_old:
        try:
            if destination.exists():
                os.remove(str(destination))
        except PermissionError as e:
            print(e)

    output = True
    try:
        shutil.move(str(source), str(destination))
    except IOError as e:
        print(e)
        output = False
    except TypeError as e:
        print(e)
        output = False
        raise

    return output


def copy_and_rename(source, destination, remove_old):
    """
    move from the download directory to working directory and rename

    :param source: Path to source file
    :param destination: Path name for destination
    :param remove_old: boolean to remove duplicate destination
    :return boolean:
    """
    if remove_old:
        try:
            if destination.exists():
                os.remove(str(destination))
        except PermissionError as e:
            print(e)

    output = True
    try:
        shutil.copy(str(source), str(destination))
    except IOError as e:
        print(e)
        output = False
    except TypeError as e:
        print(e)
        output = False
        raise

    return output


def move_slc_download(my_window):
    """
    move the downloaded, generic named file to our directory and rename

    :return:
    """
    source = locate_downloaded_lsr()
    # seem to be getting strange extension now so look first for the normal name and if now found
    # add on the extra suffix
    if not source.exists():
        source = source.with_suffix('.csv.crdownload')
        if not source.exists():
            my_window.set_status('Failed to find file ' + str(source))
            return

    destination = data_download_directory()
    destination = destination.joinpath(build_lsr_name(my_window.my_data.next_month))
    move_and_rename(source, destination, True)


def build_stake_month_name(current_date):
    """
    stake name with month and year

    :param current_date: date to build for
    :return string: file name
    """
    this_month = current_date.strftime('%Y%m')
    fn = ('Stake_' + this_month + '.pdf')
    return fn


def build_stake_report_name(current_date):
    """
    build name, including path, for stake report

    :param current_date: date to build report for
    :return string: file name, with path
    """
    fn = build_path_to_report_directory()
    return str(fn.joinpath(build_stake_month_name(current_date)))
