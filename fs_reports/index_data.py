"""Class to store database and associated items"""
# system imports
from dateutil.rrule import rrule, MONTHLY
import datetime
import calendar
import configparser

# package imports
import pandas as pd
import numpy as np

# module imports
import fs_reports.files as files
# import fs_indexing.main_window as main_window


class IndexerValues:
    """ keeps track of the database and the associated data

    """
    # fixed values for all instances of the class
    date_format = "%Y-%m-%d"

    # Column headers
    header = ["Sequence", "Ward", "Name", "Indexed", "Arbitrated"]
    hdr_date = 0
    hdr_ward = 2
    hdr_name = 3
    hdr_indexed = 4
    hdr_arb = 5
    hdr_sequence = 1

    _fn = '../data/saved.ini'
    _df = 'DEFAULT'
    _un = 'User'
    _sn = 'Stakename'
    _tm = 'ToEmail'
    _fm = 'FromEmail'

    def __init__(self):
        """ initialize the class

        """
        self.current_table = pd.DataFrame([1], index=[1])
        self.ward_list = []
        self.list_of_months = []
        self.sorted_wards = []
        self.year_count = 0

        # format for dates in the database
        self.first_month = datetime.datetime.now()
        self.last_month = datetime.datetime.now()
        self.next_month = datetime.datetime.now()

        self.username = ""
        self.password = ""
        self.stake_name = ""
        self.to_email = []
        self.from_email = []

        self.month_data = []
        self.bad_wards = []

        # read the ini data for username etc
        self.read_ini()

    def read_table(self):
        """
        Read table using fixed name

        :return:
        """
        return self.read_table_name(files.build_table_name())

    def read_table_name(self, file_name):
        """
        read the CSV file and create the table

        After reading in the table set the indexes and calculate the ward list and other items

        :param file_name: file name to load and use
        :return:
        """
        # Coerce the data into a datetimeindex and also create a month and year column
        temp_df = pd.read_csv(file_name, index_col=0)
        # TODO handle when the file isn't found

        temp_df['Date2'] = pd.to_datetime(temp_df.index, format=self.date_format)
        temp_df = temp_df.drop('Date')
        temp_df = temp_df.rename(columns={'Date2': 'Date'})
        self.current_table = temp_df.set_index(pd.DatetimeIndex(temp_df.Date))
        self.current_table['Month'] = self.current_table.index.month
        self.current_table['Year'] = self.current_table.index.year

        self.calculate_ward_data()
        return self.current_table

    def calculate_ward_data(self):
        """
        calculate the ward list and other set values

        :return:
        :rtype:
        """

        # get the list of wards in the dataset
        self.get_ward_list()
        self.get_year_count()
        self.build_list_of_dates_by_month()
        self.sort_wards()

    def get_ward_list(self):
        """ get the ward list

        :return ward_list: list of wards
        """
        ward_group = self.current_table.groupby(['Ward'])
        self.ward_list = ward_group['Ward'].unique()
        return self.ward_list

    def ward_slice(self, ward):
        """
        given dataframe create new dataframe with only the indicated ward

        :rtype: dataframe
        :param df:
        :param ward:
        :return df: dataframe with only the indicated ward
        """
        return self.current_table[self.current_table.Ward.isin([ward])]

    def get_year_count(self):
        """ Get the count of years in the dataframe

        :return years: number of years in dataframe
        """
        ward_group = self.current_table.groupby(['Year'])
        self.year_count = ward_group['Year'].unique().count()
        return self.year_count

    def build_list_of_dates_by_month(self):
        """
        count the number of months and create the list of months

        :return list: list of datetimes from the start month to the last month
        """
        temp_date = self.current_table.head(1).Date
        self.first_month = temp_date[0]
        temp_date = self.current_table.tail(1).Date
        self.last_month = temp_date[0]
        self.next_month = self.add_month(self.last_month)
        self.list_of_months = [dt for dt in rrule(MONTHLY, dtstart=self.first_month, until=self.last_month)]
        return self.list_of_months

    def sort_wards(self):
        """
        sort the wards by the overall number of indexed names

        :return list: ward list in sorted order
        """
        group = self.current_table.groupby('Ward')
        ward_series = group.Indexed.sum()
        ward_series.sort_values(axis=0, ascending=False, inplace=True)
        self.sorted_wards = np.array(ward_series.index)
        return self.sorted_wards

    def write_table(self):
        """
        write the dataframe to the csv file

        :return:
        """
        self.write_table_filename(files.build_table_name())

    def write_table_filename(self, filename):
        """
        write the CSV file from the current table

        :param filename: string filename to write
        :return:
        """
        # any cleanup or manipulation for the table goes here
        self.current_table.to_csv(filename, columns=self.header, date_format=self.date_format)

    def load_this_month(self, month_to_load):
        """
        Load download month data an add to current table using default file name

        :param month_to_load: date of month to load

        :return:
        """
        return self.load_this_month_file(files.build_lsr_path(month_to_load), month_to_load)

    def load_this_month_file(self, filename, month_to_load):
        """
        Get the CSV file from the downloads director and put it into table

        given the format of the file from familysearch, reading each line of the file
        and then doing the magic formatting is much better than simply reading in the file
        and attempting to message the file inside the dataframe

        :param filename: filename and path to load
        :rtype object: new dataframe
        :param month_to_load: date to execute on
        :return:
        """
        if self.check_for_month(month_to_load):
            return None

        # build up the download directory (our file should be there)
        df = pd.read_csv(filename)

        # give the first column a better name for convenience
        df.rename(columns={'Unnamed: 0': 'Desc'}, inplace=True)

        # create a mask for the Ward Summary lines
        ws_mask = df.Desc == 'Ward Summary'

        # create a ward_name column that has names only for Ward Summary lines
        df['Ward'] = np.where(ws_mask, df.Name, np.nan)

        # forward fill the missing ward names from the previous summary line
        df.Ward.fillna(method='ffill', inplace=True)

        # get rid of the ward summary lines
        df = df.ix[~ws_mask]

        # get rid of the Desc column
        if 'Desc' in df.columns:
            df = df.drop('Desc', axis=1)
        if 'Redo Batches' in df.columns:
            df = df.drop('Redo Batches', axis=1)

        # create the month column
        df['Date'] = self.next_month
        df = df.set_index(pd.DatetimeIndex(df['Date']))
        df['Month'] = df.index.month
        df['Year'] = df.index.year

        # create the sequence column
        last = self.current_table.tail(1)
        max_seq = int(last.iloc[0]['Sequence']) + 1
        new_sequence = np.arange(max_seq, max_seq + len(df.index))
        df['Sequence'] = new_sequence

        """ before merging this new month (in variable df) to the main table we need to make sure either
        all the ward names match or rename the new ones to correct ones.

        This occurs because FamilySearch allows individuals to pick their ward name.

        In the previous incarnation did the cleanup right here. That created a loop where this file had to
        call back into the window driver. The change now is to simply save the month data and the unknown names
        and have the window driver call the final cleanup routine.

        This refactor will help make the code cleaner, it will allow for better testing as the partial results
        of month data and unknown names are now possible to test.
        """

        # this returns just the items that differences fro the data_table
        unknown_wards = df[~df.Ward.isin(self.current_table.Ward)]['Ward'].unique()
        self.month_data = df

        if len(unknown_wards) > 0:
            # setup window to fix names
            self.bad_wards = unknown_wards
        else:
            self.bad_wards = None

        return df

    def merge_month_to_table(self):
        """ merge the current month into the main table

        """
        # concatenate downloaded month into full table
        frames = [self.current_table, self.month_data]
        df = pd.concat(frames)
        self.current_table = df.set_index(pd.DatetimeIndex(df.index))
        self.calculate_ward_data()

        self.month_data = None

    def check_for_month(self, month_to_load):
        """
        See if current month is already in dataframe

        :return boolean: true or false if month in dataframe
        """
        tail = self.current_table.tail(1)
        rc = False
        if tail.Year[0] == month_to_load.year and tail.Month[0] == month_to_load.month:
            rc = True
            # gc.status_message = str(gc.current_month.strftime('%Y %m ') + 'already in table.')
        return rc

    def add_month(self, date):
        """add one month to date, maybe falling to last day of month

        :param datetime.datetime date: the date

        ::
          >>> add_month(datetime(2014,1,31))
          datetime.datetime(2014, 2, 28, 0, 0)
          >>> add_month(datetime(2014,12,30))
          datetime.datetime(2015, 1, 30, 0, 0)
        """
        # number of days this month
        month_days = calendar.monthrange(date.year, date.month)[1]
        candidate = date + datetime.timedelta(days=month_days)
        # but maybe we are a month too far
        if candidate.day != date.day:
            # go to last day of next month,
            # by getting one day before begin of candidate month
            return candidate.replace(day=1) - datetime.timedelta(days=1)
        else:
            return candidate

    def write_ini(self):
        """
        write the ini file using default filename

        :return:
        """
        self.write_ini_filename(self._fn)

    def write_ini_filename(self, fn):
        """
        write ini file using passed filename

        Using passed file name allows for testing to use non-production temp files

        :param fn: filename to open and write
        :return:
        """
        try:
            with open(fn, 'w') as fh:
                self.write_ini_handle(fh)
        except ValueError as err:
            print(err.args)

    def write_ini_handle(self, fh):
        """
        write the values to the file given a file handle

        file previously opened and allows for use of test and production file names with no changes in this
        function

        :param fh: file handle, passed to enable unittest
        :return:
        """
        config = configparser.ConfigParser()

        # create the default section
        config[self._df] = {
            self._un: self.username,
            self._sn: self.stake_name,
            self._tm: self.to_email,
            self._fm: self.from_email
        }
        config.write(fh)

    def read_ini(self):
        """
        read ini file using default file name

        :return:
        """
        self.read_ini_filename(self._fn)

    def read_ini_filename(self, fn):
        """
        Read ini file using passed in file name

        allows for testing using a different file name and directory

        :param fn: file name to open and read
        :return:
        """
        try:
            with open(fn, 'r') as fh:
                self.read_ini_handle(fh)
        except ValueError as err:
            print(err.args)

    def read_ini_handle(self, fh):
        """
        Process ini file from file handle

        :param fh: file handle of file to read
        :return:
        """
        config = configparser.ConfigParser()
        # config.read(file_name)
        config.read_file(fh)
        self.username = config[self._df][self._un]
        self.stake_name = config[self._df][self._sn]
        self.to_email = config[self._df][self._tm]
        self.from_email = config[self._df][self._fm]

    def counts_by_date(self, df, columns):
        """
        Create dataframe with unique counts

        dataframe is passed instead of using current_table so that can work on the ward slices instead
        of the entire dataframe

        :param df: dataframe to count
        :param columns: column to count on
        :return dataframe: counted dataframe
        """
        # group then count by month then pivot
        df_group = df.groupby(['Date'])
        df_counts = df_group.Month.value_counts()
        df_counts.columns = columns
        df_counts.index = df_counts.index.droplevel(1)
        return df_counts

    def sums_by_date(self, df, column_label):
        """
        create data frame by values

        :param df: dataframe to use
        :param column_label: column to sum on
        :return Series: series with date and sum value
        """
        return self.sum_slicer(df, 'Date', column_label)

    def sum_slicer(self, df, group_by, column_label):
        """
        Slice the df by the group and sum on the column label

        :param df: dataframe to slice
        :param group_by: which columns to group by
        :param column_label: column to sum on
        :return:
        """
        first_group_by = df.groupby(group_by)
        first_group_sum = first_group_by.sum()
        first_group_sum = first_group_sum[column_label]
        full_list = first_group_sum.reindex(self.list_of_months, fill_value=0)
        return full_list

    def ward_month_sum(self, stake_year=None):
        """
        Create the dataframe for the monthly pie chart using the class dataframe

        ward units are sorted by the year total values

        dataframe looks like
                indexed
        ward
        Hazeldale 3113
        Murrayhill 8447
        ...

        :param stake_year: dataframe sorted according to year totals
        :return dataframe: sorted by count dataframe
        """
        ward_group = self.current_table.groupby(['Ward', 'Month', 'Year'])
        ward_totals = ward_group.sum()
        ward_totals = ward_totals[['Indexed']]

        # now slice through and just take our month and year
        stake_month = ward_totals.xs((self.last_month.year,
                                      self.last_month.month),
                                     level=(2, 1))
        # sort by indexed values or the year dataframe
        if stake_year is None:
            stake_month = stake_month.sort_values(by='Indexed', ascending=False)
        else:
            # in this case we want to match the sorting from the stake_year so that our labels and legend
            # can apply to both pie charts
            t1 = stake_month.loc[stake_year['Indexed'].argsort().index].dropna()
            stake_month = t1

        return stake_month

    def ward_year_sum(self):
        """
        Create the dataframe for the year pie

        dataframe looks like
                indexed
        ward
        Hazeldale 110663
        Murrayhill 71444

        :return dataframe: created dataframe
        """
        ward_group = self.current_table.groupby(['Ward', 'Year'])
        ward_totals = ward_group.sum()
        ward_totals = ward_totals[['Indexed']]
        stake_year = ward_totals.xs(self.last_month.year, level=1)
        stake_year = stake_year.sort_values(by='Indexed', ascending=False)
        return stake_year

    def ward_count_arrays(self, column):
        """
        create nested array of counts for each ward by month

        :param df: dataframe to extract dates and counts from
        :param column: Indexed or Arbitrated
        :return count_array: array for each ward with monthly count in each array
        """
        count_array = None
        for idx, ward in enumerate(self.sorted_wards):
            ward_slice_df = self.ward_slice(ward)
            ward_values = np.array(self.sums_by_date(ward_slice_df, column))
            if count_array is None:
                count_array = ward_values
            else:
                count_array = np.vstack((count_array, ward_values))
        return count_array

    def individual_list(self, df, months, max_size, column):
        """
        Create list of individuals (first and last only no middle names)

        :param df: dataframe to use
        :param months: int how many months to go back
        :param max_size: int maximum number of lines in list
        :param column: string for total_count or arbitrated
        :return:
        """
        individuals = df.loc[df.index.to_period('M')
                             .isin(df.index.to_period('M').unique()[-months:])]
        individuals = individuals.groupby(['Name'])[column].sum().reset_index()
        individuals = individuals[individuals[column] > 0]
        individuals = individuals.sort_values(by=column, ascending=False)
        if len(individuals) > max_size:
            # list too long get sums and then create extra line
            sums = individuals.sum()
            total_count = sums[column]
            remaining = len(individuals) - max_size

            short_list = individuals[:max_size]
            short_list_sum = short_list.sum()
            remaining_indexed = total_count - short_list_sum[column]
            t1 = short_list.iloc[max_size - 1]
            t1.iloc[0] = "Remaining " + str(remaining)
            t1.iloc[1] += remaining_indexed
            short_list.iloc[max_size - 1] = t1
            individuals = short_list

        return individuals
