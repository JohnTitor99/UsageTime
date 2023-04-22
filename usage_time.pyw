from datetime import datetime, timedelta
from time import sleep
import psutil
import pandas as pd

from get_statistics import GetStatistics
from config import *


class UsageTime(object):
    def __init__(self):
        self.now_start = None
        self.now_end = None
        self.ses_duration = None

    # check the process is running; 
    def start_session(self):
        processes = []
        while True:
            for proc in psutil.process_iter():
                processes.append(proc.name())
            if PROC_NAME in processes:
                self.now_start = datetime.now()
                print('started...')
                self.end_session()
                break
            else:
                processes.clear()
                sleep(1)
                continue


    # check the process is stopped; if it stopped, it will perform all calculations and write data in files
    def end_session(self):
        processes = []
        while True:
            for proc in psutil.process_iter():
                processes.append(proc.name())
            if PROC_NAME not in processes:
                self.now_end = datetime.now()
                self.get_session_duration()
                self.get_statistics()
                print('end.')
                break
            else:
                # write date if it's 00:00
                if self.now_start.date() != datetime.now().date():
                    self.now_end = datetime.now()
                    self.get_session_duration()
                    self.get_statistics()
                    self.now_start = datetime.now()
                    print('00:00')
                processes.clear()
                sleep(1)
                continue        
        

    def get_session_duration(self):
        current_date = self.now_start.date()   # date for session duration
        time_duration = str(self.now_end - self.now_start).split(".")[0]
        if len(time_duration) < 8: time_duration = '0' + time_duration # add 0 to hour value

        self.write_usage_time(current_date, time_duration)


    def write_usage_time(self, current_date, time_duration):
        df = pd.DataFrame()

        # get df from the file or adding columns and first row if file is empty
        try:
            df = pd.read_csv('UsageTime/usage_time.csv')
            # add first row if no rows yet
            if len(df) == 0:
                df.loc[0] = [str(current_date), '00:00:00']
        except:
            # add columns and first row
            df['Date'] = None
            df['UsageTime'] = None
            df.loc[0] = [str(current_date), '00:00:00']

        last_date = datetime.strptime(df.loc[0, 'Date'], '%Y-%m-%d')
        days_amount = (self.now_end.date() - last_date.date()).days

        # update today's usage time
        if days_amount == 0:
            # add a duration of current session to a previous today's session
            prev_time_list = df.iloc[0]['UsageTime'].split(':')
            curr_time_list = time_duration.split(':')
            prev_sess_seconds = (int(prev_time_list[0])*60*60) + (int(prev_time_list[1])*60) + int(prev_time_list[2])
            curr_sess_seconds = (int(curr_time_list[0])*60*60) + (int(curr_time_list[1])*60) + int(curr_time_list[2])
            total_time_tuple = next(self.transform(prev_sess_seconds + curr_sess_seconds))
            total_time = f"{total_time_tuple[0]}:{total_time_tuple[1]}:{total_time_tuple[2]}"
            if len(total_time) < 8: total_time = '0' + total_time # add 0 to hour value
            
            # delete first row and write new one
            df.drop(df.head(1).index, inplace=True)
            df.loc[-1] = [str(current_date), total_time]  # adding a row
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True) 

            df.to_csv(f"UsageTime/{FILENAME}.csv", mode='w', index=False)
            df.to_string(f"UsageTime/{FILENAME}.txt", index=False)

        # add new_row and missing days
        elif days_amount > 0:
            date_diff = (self.now_end - last_date).days # a count of missing days
            for i in range(date_diff):
                # add missing days if there are
                if str(current_date) != str(last_date + timedelta(days=i+1)).split(' ')[0]:
                    missed_day = str(last_date + timedelta(days=i+1)).split(' ')[0]
                    missed_time = str(last_date + timedelta(days=i+1)).split(' ')[1]
                    df.loc[-1] = [missed_day, missed_time]  # adding a row
                    df.index = df.index + 1  # shifting index
                    df.sort_index(inplace=True)
                # add today usage time
                else:
                    df.loc[-1] = [str(current_date), time_duration]  # adding a row
                    df.index = df.index + 1  # shifting index
                    df.sort_index(inplace=True)

            df.to_csv(f"UsageTime/{FILENAME}.csv", mode='w', index=False)
            df.to_string(f"UsageTime/{FILENAME}.txt", index=False)
            

    # transform seconds into hours, minutes and seconds
    def transform(self, n):
        n = n   # seconds, which we need to convert
        full_min = n // 60
        hour = full_min // 60 # hours
        min = full_min % 60 # minutes
        sec = n % 60 # seconds
        if len(str(min)) < 2: min = '0' + str(min)
        if len(str(sec)) < 2: sec = '0' + str(sec)
            
        yield hour, min, sec


    def get_statistics(self):
        if GET_STATISCICS:
            gs = GetStatistics()
            gs.get_statistics()



if __name__ == '__main__':
    ut = UsageTime()
    ut.start_session()