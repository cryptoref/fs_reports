"""
Create all of the output, graphs and text.

"""

# system imports
import itertools
# package imports
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid_spec
import matplotlib.patches as mp_patches
import matplotlib.dates as mdates
from matplotlib import cm

# module imports
from fs_admin_reports import globalconfig as gc

month_labels = "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
month_list = np.r_[1:13]
month_bar_width = .35


def dataframe_sum(group_by, column_label, reset_index):
    """
    Create dataframe with cumulative totals for column

    :param group_by: list of columns to group by
    :param column_label: list of columns to sum (this is always a single element
    :param reset_index: list of columns to reset the index to
    :return pivot dataframe:
    """
    # group by the requested group and then sum for the column
    first_group_by = gc.data_table.groupby(group_by)
    first_group_sum = first_group_by.sum()
    first_group_sum = first_group_sum[column_label]

    # create bar chart on ax1
    first_group_pivot = first_group_sum.reset_index().pivot(*reset_index)
    pivot_cumulative = first_group_pivot.cumsum(axis=1)
    return first_group_pivot


def bar_with_table(ax1, ax2, df, chart_style, ax1_title,
                   ax2_title):
    """
    Create year over year bar chart with underlying table, 2nd axis for running total

    Two charts in one call as the setup for both is almost exactly the same. If there is no need for the
    running total then send in ax2 as None

    :param ax1: axis to generate YOY bar chart
    :param ax2: axis to generate cumulative line chart
    :param df: dataframe to chart
    :param df_cum: dataframe with
    :param chart_style: matplotlib style to govern all but colors
    :param ax1_title: title for chart on axis 1
    :param ax2_title: title for chart on axis 2
    :return:
    """

    cell_text = []
    row_labels = []
    row_colors = []
    bar_start = np.arange(len(month_list))
    bar_width = (bar_start[1] - bar_start[0]) * 0.7
    row_bottom = np.zeros(len(month_list))

    with plt.style.context(chart_style):

        idx = 0
        for current_year, row in df.iterrows():
            row_values = row.values.astype(int).tolist()
            current_color = gc.bar_colors[idx]
            ax1.bar(bar_start, row_values, width=bar_width,
                    bottom=row_bottom,
                    color=current_color)
            row_bottom = row_bottom + row_values
            row_colors.append(current_color)
            cell_text.append(row_values)
            row_labels.append(str(current_year))
            idx += 1

        ax1.set_title(ax1_title)
        ax1.set_xticks([])

        tbl = ax1.table(cellText=cell_text, rowLabels=row_labels,
                        loc='bottom', colLabels=month_labels,
                        rowColours=row_colors)
        # table_properties = tbl.properties()
        # fix our sizing here
        # tbl.update(table_properties)

        cell_text = []
        row_labels = []
        row_colors = []
        if ax2 is not None:
            # create running total YoY
            # line chart
            # goes into ax2
            idx = 0
            pivot_cumulative = df.cumsum(axis=1)

            for current_year, row in pivot_cumulative.iterrows():
                row_values = row.values.astype(int).tolist()
                current_color = gc.line_colors[idx]
                ax2.plot(month_list, row_values, marker='o', color=gc.line_colors[idx])
                row_colors.append(current_color)
                cell_text.append(row_values)
                row_labels.append(str(current_year))
                idx += 1
            ax2.set_title(ax2_title)
            ax2.set_xticks([])
            tbl = ax2.table(cellText=cell_text, rowLabels=row_labels,
                            loc='bottom', colLabels=month_labels,
                            rowColours=row_colors)

    # get total number so that can subtract to obtain number added by those outside top 20
    # last = first_group_sum.tail(1)
    # month_aggregate = int(last.iloc[0]['Indexed']) + 1


def create_stake_yoy(ax1, ax2=None):
    """
    Create stake year over year chart and cumulative YoY chart

    Two charts in one call as the setup for both is almost exactly the same

    :param ax1: axis to generate YOY bar chart
    :param ax2: axis to generate cumulative chart
    :return:
    """

    group_by = ['Month', 'Year']
    column_label = ['Indexed']
    reset_index = ['Year', 'Month', 'Indexed']
    chart_style = 'fivethirtyeight'
    ax1_title = 'Indexing by Month'
    ax2_title = 'Indexing Running Total'

    df = dataframe_sum(group_by, column_label, reset_index)
    bar_with_table(ax1, ax2, df, chart_style,
                   ax1_title, ax2_title)


def dataframe_counts(group_by, columns, reset_index):
    """
    Create dataframe with unique counts

    :param group_by: list of columns to group
    :param columns: list of columns to count
    :param reset_index: list of columns to pivot on
    :return dataframe: pivoted count dataframe
    """
    # group then count by month then pivot
    df_group = gc.data_table.groupby(group_by)
    df_counts = df_group.Month.value_counts()
    df_counts.columns = columns

    df_pivot = df_counts.reset_index().pivot(*reset_index)
    return df_pivot


def create_indexers_dataframe():
    """
    Create the dataframe for the indexers

    create the total of indexers

          jan  feb  mar
    2013   15   41   45
    2014   27   33   31
    2015   37   53   42

    :return dataframe: the indexers by year and month
    """
    group_by = ['Year']
    columns = ['Month', 'Indexers']
    reset_index = ['Year', 'Month']
    return dataframe_counts(group_by, columns, reset_index)


def individual_list(months, max_size, column):
    """
    Create the three lists of individuals month, 3 and 6 months

    :param months: int how many months to go back
    :param max_size: int maximum number of lines in list
    :param column: string for total_count or arbitrated
    :return:
    """

    period_df = gc.data_table.index.to_period('M')
    individuals = gc.data_table.loc[gc.data_table.index.to_period('M')
                                    .isin(gc.data_table.index.to_period('M').unique()[-months:])]
    individuals = individuals.groupby(['Name'])[column].sum().reset_index()
    individuals = individuals[individuals[column] > 0]
    individuals = individuals.sort_values(by=column, ascending=False)
    if len(individuals) > max_size:
        # list too long get sums and then create extra line
        sums = individuals.sum()
        total_count = sums[column]

        short_list = individuals[:max_size]
        short_list_sum = short_list.sum()
        remaining_indexed = total_count - short_list_sum[column]
        t1 = short_list.iloc[max_size-1]
        t1.iloc[0] = "Remaining"
        t1.iloc[1] += remaining_indexed
        short_list.iloc[max_size - 1] = t1
        individuals = short_list

    return individuals


def build_list_table(ax, df_month, column, title):
    """
    build table with 3 sections each having name and count

    :param ax: axis that will contain table
    :param df_month: dataframe holding list of individuals
    :param column: column in use Indexed Arbitrated
    :return:
    """
    cell_text = []
    row_labels = []
    row_colors = []
    idx = 0

    name_list = []
    full_names = df_month['Name'].values.tolist()
    for idx, this_name in enumerate(full_names):
        if len(this_name.split()) > 2:
            split_name = this_name.split()
            name_list.append(split_name[0] + " " + split_name[2])
        else:
            name_list.append(this_name)

    count_list = df_month[column].values.tolist()
    rows = list(zip(name_list, count_list))

    # create a list from the dataframe
    # this plot is a total cheat - table location VERY hard without chart so create one
    # and make it invisible. Now can set table location and it all works right
    # i'd call this a bug
    ax.plot([0], color='w')
    ax.set_title(title)
    tbl = ax.table(cellText=rows, loc='upper left', colWidths=[0.75, 0.25])
    properties = tbl.properties()
    cell_dict = tbl.get_celld()

    # cellDict=the_table.get_celld()
    # cellDict[(0,0)].set_width(0.1)

    tbl.set_fontsize(14)
    ax.set_xticks([])
    ax.set_yticks([])


def create_indexers(ax1, ax2, ax3, ax4):
    """
    List the number of indexers per month

    :param ax1: axis to build bar chart
    :param ax2: axis for current month individual list
    :param ax3: axis for 3 month individual list
    :param ax4: axis for 6 month individual list
    :return:
    """
    by_year = create_indexers_dataframe()
    bar_with_table(ax1, None, by_year, 'fivethirtyeight', 'Indexers', "")

    list_1month = individual_list(1, 11, 'Indexed')
    list_3month = individual_list(3, 11, 'Indexed')
    list_6month = individual_list(6, 11, 'Indexed')

    month_title = 'Indexers for ' +  gc.current_month.strftime("%B %Y")
    build_list_table(ax2, list_1month, 'Indexed', month_title)
    build_list_table(ax3, list_3month, 'Indexed', 'Last 3 Months')
    build_list_table(ax4, list_6month, 'Indexed', 'Last 6 Months')


def create_arbitrators_dataframe():
    """
    Create the dataframe for the indexers

    create the total of indexers

          jan  feb  mar
    2013   15   41   45
    2014   27   33   31
    2015   37   53   42

    :return dataframe: the indexers by year and month
    """
    group_by = ['Month', 'Year']
    column_label = ['Arbitrated']
    reset_index = ['Year', 'Month', 'Arbitrated']
    return dataframe_sum(group_by, column_label, reset_index)


def create_arbitrators(ax1, ax2, ax3, ax4):
    """
    create the total of arbitrators

    :param ax1: axis on which to generate chart
    :param ax2: axis to store month list of arbs
    :param ax3: axis to store 3 month list
    :param ax4: axis to store 6 month list
    :return:
    """
    by_year = create_arbitrators_dataframe()
    bar_with_table(ax1, None, by_year, 'fivethirtyeight', 'Arbitrated', "")

    list_1month = individual_list(1, 11, 'Arbitrated')
    list_3month = individual_list(3, 11, 'Arbitrated')
    list_6month = individual_list(6, 11, 'Arbitrated')

    month_title = 'Arbitration for ' +  gc.current_month.strftime("%B %Y")
    build_list_table(ax2, list_1month, 'Arbitrated', month_title)
    build_list_table(ax3, list_3month, 'Arbitrated', 'Last 3 months')
    build_list_table(ax4, list_6month, 'Arbitrated', 'Last 6 months')


def pie_legends(pie1, pie2):
    """
    create the legend for the pie charts

    :param pie1: pie chart for the first
    :param pie2:
    :return:
    """
    plt.legend(handles=[pie1, pie2])


def create_month_pie_dataframe(stake_year=None):
    """
    Create the dataframe for the monthly pie chart using the data frame in gc.dataframe

    :param stake_year: dataframe sorted according to year totals
    :return dataframe: sorted by count dataframe
    """
    ward_group = gc.data_table.groupby(['Ward', 'Month', 'Year'])
    ward_totals = ward_group.sum()
    ward_totals = ward_totals[['Indexed']]

    # now slice through and just take our month and year
    stake_month = ward_totals.xs((gc.current_month.year, gc.current_month.month), level=(2, 1))
    # sort by indexed values or the year dataframe
    if stake_year is None:
        stake_month = stake_month.sort_values(by='Indexed', ascending=False)
    else:
        # in this case we want to match the sorting from the stake_year so that our labels and legend
        # can apply to both pie charts
        t1 = stake_month.loc[stake_year['Indexed'].argsort().index].dropna()
        stake_month = t1

    return stake_month


def create_month_pie(ax4, stake_year=None):
    """
    Create pie percentage for month

    :param ax4: axis on which to generate chart
    :param stake_year: dataframe with year order and colors
    :return:
    """
    # create ward percentages Month
    # pie chart
    # goes into ax4
    # group by the ward month and year use this grouping to get the current month rankings
    stake_month = create_month_pie_dataframe(stake_year)

    ax4.pie(stake_month['Indexed'], autopct=pie_auto_percent, colors=gc.pie_colors,
            shadow=True, startangle=90)
    ax4.axis('equal')
    ax4.set_title('Month Percent')


def create_year_pie_dataframe():
    """
    Create the dataframe for the year pie

    :return dataframe: created dataframe
    """
    ward_group = gc.data_table.groupby(['Ward', 'Year'])
    ward_totals = ward_group.sum()
    ward_totals = ward_totals[['Indexed']]
    stake_year = ward_totals.xs(gc.current_month.year, level=1)
    stake_year = stake_year.sort_values(by='Indexed', ascending=False)
    return stake_year


def pie_auto_percent(pct):
    return ('%.0f%%' % pct) if pct > 10 else ''


def create_year_pie(ax5):
    """
    Create pie percentage year to date

    :param ax5: axis on which to generate chart
    :return dataframe: sorted dataframe
    """
    stake_year = create_year_pie_dataframe()

    ax5.pie(stake_year['Indexed'], autopct=pie_auto_percent, colors=gc.pie_colors,
            shadow=True, startangle=90)
    ax5.set_title('Year Percent')
    ax5.axis('equal')

    return stake_year


def inner_patch_lister(ward, color_cycle):
    """
    inside the list comprehension to make the patch

    :param ward: ward string for the label
    :param color_cycle: color for marker
    :return patch: created patch
    """
    # return mp_patches.Patch(color=colors.hex2color(next(color_cycle)['color']), label=ward)
    # return mp_patches.Patch(color=next(color_cycle), label=ward)
    return mp_patches.Patch(color=color_cycle, label=ward)


def patch_lister(stake_year):
    """
    Create the patches that form the legend

    :param stake_year:
    :return:
    """

    lab1 = [x for x in stake_year.index]
    patches = [inner_patch_lister(label, gc.pie_colors[idx]) for idx, label in enumerate(lab1)]

    plt.legend(handles=patches, loc=3,
               bbox_to_anchor=(-1.2, -.3), ncol=3)
    return patches


def create_pies(ax4, ax5):
    """
    Create the two pie charts

    :param ax4: first pie chart
    :param ax5: second pie chart
    :return:
    """
    with plt.style.context('fivethirtyeight'):

        # do year first as that will set the order for doing the legend and month
        stake_year = create_year_pie(ax5)
        create_month_pie(ax4, stake_year)
        patch_lister(stake_year)


def color_mapping(number_of_wards, number_of_years):
    """
    Create our color map based on the number of wards

    :param number_of_wards: how many wards in dataframe
    :param number_of_years: how many years in dataframe
    :return:
    """
    start = 0.0
    stop = 1.0
    cm_subsection = np.linspace(start, stop, number_of_wards)
    gc.pie_colors = [cm.Dark2(x) for x in cm_subsection]
    # gc.pie_colors = [cm.hsv(x) for x in cm_subsection]

    cm_subsection = np.linspace(0.2, stop, number_of_years)
    gc.bar_colors = [cm.winter(x) for x in cm_subsection]
    gc.line_colors = [cm.winter(x) for x in cm_subsection]


def create_stake_report():
    """
    Creates the stake report (3 pages)

    Page 1 grid layout is as follows
    +----------------------------------+
    |         ax1 (YoY Bar)            |
    +----------------------------------+
    +----------------------------------+
    |          ax2 running             |
    +----------------------------------+
    +---------------++-----------------+
    | ax3 pie month || ax4 pie year    |
    +---------------++-----------------+

    Page 2 grid layout
    +----------------------------------+
    |          ax5 indexers            |
    +----------------------------------+
    +----------------------------------+
    |         Top 20 indexers          |
    +----------------------------------+

    Page 3 grid layout
    +----------------------------------+
    |       ax6 Arbitration Bar        |
    +----------------------------------+
    +---------------++-----------------+
    |       Arbitration list           |
    +---------------++-----------------+

    :rtype: object
    :return:
    """

    # first establish the grid for where each plot will go
    # clean up any other plots that may be active
    plt.close('all')

    # turn interactive on right now
    plt.ion()

    color_mapping(len(gc.ward_list), gc.year_count)

    with PdfPages('../reports/stake.pdf') as pdf:
        fig = plt.figure(figsize=(8.5, 11))

        gs = grid_spec.GridSpec(6, 2)
        ax1 = plt.subplot(gs[0:2, 0:])
        ax2 = plt.subplot(gs[2:4, 0:])
        ax3 = plt.subplot(gs[4:6, 0])
        ax4 = plt.subplot(gs[4:6, 1])

        current_bbox = ax1.get_position()
        bottom_of_1 = current_bbox.y0
        current_bbox.y0 += (1 - current_bbox.y0) * .25
        ax1.set_position(current_bbox)

        current_bbox = ax2.get_position()
        current_bbox.y0 += (bottom_of_1 - current_bbox.y0) * .25
        ax2.set_position(current_bbox)

        # create page 1 charts
        create_stake_yoy(ax1, ax2)
        create_pies(ax3, ax4)

        # do not do tight_layout as with the movement of the bbox tight messes things up
        pdf.savefig()
        plt.close()

        # create page 2 charts
        gs = grid_spec.GridSpec(2, 3)
        ax1 = plt.subplot(gs[0, :])
        ax2 = plt.subplot(gs[1, 0], axisbg='white')
        ax3 = plt.subplot(gs[1, 1], axisbg='white')
        ax4 = plt.subplot(gs[1, 2], axisbg='white')

        current_bbox = ax1.get_position()
        bottom_of_1 = current_bbox.y0
        current_bbox.y0 += (1 - current_bbox.y0) * .25
        ax1.set_position(current_bbox)

        create_indexers(ax1, ax2, ax3, ax4)

        pdf.savefig()
        plt.close()

        # create page 3 charts
        gs = grid_spec.GridSpec(2, 3)
        ax1 = plt.subplot(gs[0, :])
        ax2 = plt.subplot(gs[1, 0], axisbg='white')
        ax3 = plt.subplot(gs[1, 1], axisbg='white')
        ax4 = plt.subplot(gs[1, 2], axisbg='white')

        current_bbox = ax1.get_position()
        bottom_of_1 = current_bbox.y0
        current_bbox.y0 += (1 - current_bbox.y0) * .25
        ax1.set_position(current_bbox)

        create_arbitrators(ax1, ax2, ax3, ax4)

        pdf.savefig()
        plt.show()


def values_by_date(df, column_label):
    """
    create data frame by values

    :param df: dataframe to use
    :param column_label: column to sum on
    :return dataframe: dataframe grouped by date summed using column
    """
    first_group_by = gc.data_table.groupby(['Date'])
    first_group_sum = first_group_by.sum()
    first_group_sum = first_group_sum[column_label]
    return first_group_sum


def counts_by_date(df, columns):
    """
    Create dataframe with unique counts

    :param df: dataframe to use
    :param columns: column to count on
    :return dataframe: counted dataframe
    """
    # group then count by month then pivot
    df_group = gc.data_table.groupby(['Date'])
    df_counts = df_group.Month.value_counts()
    df_counts.columns = columns
    df_counts.index = df_counts.index.droplevel(1)

    return df_counts


def multi_year():
    """
    Plot the data as a multi year single line


    :return:
    """

    # TODO make this two axis graph with number of entities and actual value
    # TODO add running total (maybe)

    color_mapping(len(gc.ward_list), gc.year_count)

    fig = plt.figure(figsize=(8.5, 11))

    # create page 2 charts
    gs = grid_spec.GridSpec(4, 2)
    ax1 = plt.subplot(gs[0:2, :])
    ax2 = plt.subplot(gs[2, 0], axisbg='white')
    ax3 = plt.subplot(gs[2, 1], axisbg='white')
    ax4 = plt.subplot(gs[3, 1], axisbg='white')

    chart_style = 'fivethirtyeight'
    ax1_title = gc.stakename + ' Indexed and Indexers'

    df_value = values_by_date(gc.data_table, 'Indexed')
    df_count = counts_by_date(gc.data_table, 'Indexed')

    multi_year_plot(ax1, df_value, df_count, chart_style, ax1_title)


def multi_year_plot(ax1, df_value, df_count, chart_style, ax1_title):
    """
    Create year over year bar chart with underlying table, 2nd axis for running total

    Two charts in one call as the setup for both is almost exactly the same. If there is no need for the
    running total then send in ax2 as None

    :param ax1: axis to generate YOY bar chart
    :param df_value: dataframe with summary values
    :param df_count: dataframe with number of individuals
    :param chart_style: matplotlib style to govern all but colors
    :param ax1_title: title for chart on axis 1
    :return:
    """

    cell_text = []
    row_labels = []
    row_colors = []

    with plt.style.context(chart_style):

        color0 = plt.rcParams['axes.color_cycle'][0]
        color1 = plt.rcParams['axes.color_cycle'][1]

        years = mdates.YearLocator()
        months = mdates.MonthLocator()
        years_format = mdates.DateFormatter('%Y')

        ax1.set_title(ax1_title)

        ax1_twin = ax1.twinx()

        ax1.plot(df_value.index, df_value.values)
        ax1.set_ylabel('Names Indexed', color=color1)
        ax1.tick_params(axis='y', colors=color1)

        ax1_twin.plot(df_count.index, df_count.values)
        ax1_twin.set_ylabel('Indexers', color=color0)
        ax1_twin.tick_params(axis='y', colors=color0)

        ax1.xaxis.set_major_locator(years)
        ax1.xaxis.set_major_formatter(years_format)
        ax1.xaxis.set_minor_locator(months)

        """
        idx = 0
        for current_year, row in df_value.iterrows():
            row_values = row.values.astype(int).tolist()
            current_color = gc.bar_colors[idx]
            ax1.bar(bar_start, row_values, width=bar_width,
                    bottom=row_bottom,
                    color=current_color)
            row_bottom = row_bottom + row_values
            row_colors.append(current_color)
            cell_text.append(row_values)
            row_labels.append(str(current_year))
            idx += 1

        ax1.set_title(ax1_title)
        ax1.set_xticks([])

        tbl = ax1.table(cellText=cell_text, rowLabels=row_labels,
                        loc='bottom', colLabels=month_labels,
                        rowColours=row_colors)
        # table_properties = tbl.properties()
        # fix our sizing here
        # tbl.update(table_properties)

        cell_text = []
        row_labels = []
        row_colors = []
        if ax2 is not None:
            # create running total YoY
            # line chart
            # goes into ax2
            idx = 0
            pivot_cumulative = df_value.cumsum(axis=1)

            for current_year, row in pivot_cumulative.iterrows():
                row_values = row.values.astype(int).tolist()
                current_color = gc.line_colors[idx]
                ax2.plot(month_list, row_values, marker='o', color=gc.line_colors[idx])
                row_colors.append(current_color)
                cell_text.append(row_values)
                row_labels.append(str(current_year))
                idx += 1
            ax2.set_title(ax2_title)
            ax2.set_xticks([])
            tbl = ax2.table(cellText=cell_text, rowLabels=row_labels,
                            loc='bottom', colLabels=month_labels,
                            rowColours=row_colors)

        """

    # get total number so that can subtract to obtain number added by those outside top 20
    # last = first_group_sum.tail(1)
    # month_aggregate = int(last.iloc[0]['Indexed']) + 1