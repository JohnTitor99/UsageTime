import pandas as pd

from config import *


class GetStatistics(object):
    def __init__(self):
        self.df = pd.read_csv('UsageTime/usage_time.csv')
        self.df_stats = pd.DataFrame()

        self.usage_time_dict = {} # usage time for certain period: total; per week; per month; per year
        self.average_time_dict = {} # average usage time for certain period: total; per week; per month; per year
    

    def get_statistics(self):
        self.df_stats['Name'] = None
        self.df_stats['Value'] = None

        self.get_usage_time(len(self.df), 'Total') # total usage time
        self.get_usage_time(7, 'per Week') # usage time per last week
        self.get_usage_time(30, 'per Month') # usage time per last month
        self.get_usage_time(365, 'per Year') # usage time per last year

        self.get_average_time(len(self.df), 'Total') # average usage time
        self.get_average_time(7, 'per Week') # average time per last week
        self.get_average_time(30, 'per Month') # average time per last month
        self.get_average_time(365, 'per Year') # average time per last year

        self.add_data_to_df(self.usage_time_dict)
        self.add_data_to_df(self.average_time_dict)

        self.write_data()


    def get_usage_time(self, days, period):
        time_values_list = self.df.head(days)['UsageTime'].to_list()
        # get value if there is enough data for that
        if len(time_values_list) >= days:
            total_seconds = 0
            for value in time_values_list:
                total_seconds += int(value.split(':')[0])*60*60
                total_seconds += int(value.split(':')[1])*60
                total_seconds += int(value.split(':')[2])

            total_time_tuple = next(self.transform(total_seconds))
            usage_time = f"{total_time_tuple[0]}:{total_time_tuple[1]}:{total_time_tuple[2]}"
            self.usage_time_dict['Usage time ' + period] = usage_time
        else:
            self.usage_time_dict['Usage time ' + period] = 'No data yet'


    def get_average_time(self, days, period):
        time_values_list = self.df.head(days)['UsageTime'].to_list()
        # get value in there is enough data for that
        if len(time_values_list) >= days:
            values_list = []
            for value in time_values_list:
                value_sec = 0
                value_sec += int(value.split(':')[0])*60*60
                value_sec += int(value.split(':')[1])*60
                value_sec += int(value.split(':')[2])
                values_list.append(value_sec)

            average_time_sec = next(self.transform(int(sum(values_list) / len(values_list))))
            average_time = f"{average_time_sec[0]}:{average_time_sec[1]}:{average_time_sec[2]}"
            self.average_time_dict['Average time ' + period] = average_time
        else:
            self.average_time_dict['Average time ' + period] = 'No data yet'


    # transform seconds into hours, minutes and seconds
    def transform(self, n):
        n = n   # seconds, which we need to convert
        full_min = n // 60
        hour = full_min // 60 # hours
        min = full_min % 60 # minutes
        sec = n % 60 # seconds
        if len(str(min)) < 2: min = '0' + str(min)
        if len(str(sec)) < 2: sec = '0' + str(sec)
            
        yield str(hour), str(min), str(sec)


    def add_data_to_df(self, data_dict):
        for key, value in data_dict.items():
            self.df_stats.loc[-1] = [key, value]
            self.df_stats.index = self.df_stats.index + 1  # shifting index
            self.df_stats = self.df_stats.reset_index(drop=True)

        # self.df_stats.loc[-1] = ['---', '---']
        # self.df_stats.index = self.df_stats.index + 1  # shifting index


    def write_data(self):
        self.df_stats.to_csv(f"Statistics/{STATS_FILENAME}.csv", mode='w', index=False)
        self.df_stats.to_string(f"Statistics/{STATS_FILENAME}.txt", index=False)



if __name__ == '__main__':
    gs = GetStatistics()
    gs.get_statistics()