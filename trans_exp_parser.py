import os

import numpy as np
import pandas as pd
pd.pandas.set_option('display.max_columns', None)
pd.set_option('mode.chained_assignment', None)


from datetime import datetime
from datetime import timedelta

from tqdm.auto import tqdm
tqdm.pandas()

# Import util functions
from pacsltk.pacs_util import *

def read_csv_file(csv_file):
    return pd.read_csv(csv_file, index_col=0, parse_dates=True).dropna()

def preprocess_df(df):
    epoch_millis_cols_list = ['end_time', 'start_time']
    for epoch_col in epoch_millis_cols_list:
        df[epoch_col] = df[epoch_col] / 1000

    df['client_elapsed_time'] = df['client_elapsed_time'] * 1000

    epoch_cols_list = ['client_start_time', 'client_end_time', 'end_time', 'start_time']
    for epoch_col in epoch_cols_list:
        times = df[epoch_col].apply(lambda x: datetime.fromtimestamp(x))
        times = pd.to_datetime(times.dt.to_pydatetime())
        df[epoch_col + '_dt'] = times
    
    return df

def time_preprocess_df(df):
    time_idx = df['client_start_time_dt'] - df['client_start_time_dt'].min()

    tdf = df[['is_cold', 'inst_id', 'vm_id', 'elapsed_time', 'aws_duration', 'client_elapsed_time', 'client_start_time_dt', 'client_end_time_dt']]
    tdf.index = time_idx

    return tdf, time_idx

def parse_instance_info(df, idle_mins_before_kill):
    u_instances = df['inst_id'].unique()
    all_instance_info = []
    for instance_id in (u_instances):
        sub_df = df[df['inst_id'] == instance_id].copy()
        instance_start = sub_df['client_start_time'].min()
        instance_start_dt = sub_df['client_start_time_dt'].min()
        instance_end = sub_df['client_end_time'].max()
        instance_end_dt = sub_df['client_end_time_dt'].max()
        # extended lifetime after sometime with no request
        instance_end_ext = instance_end + (idle_mins_before_kill * 60)
        instance_end_ext_dt = instance_end_dt + timedelta(minutes=idle_mins_before_kill)
        lifetime_mins = (instance_end - instance_start) / 60
        lifetime_mins_ext = lifetime_mins + idle_mins_before_kill
        
        #running_time_mins = sub_df.loc[:,'elapsed_time'].sum() / 1000 / 60
        running_time_mins = sub_df.loc[:,'client_elapsed_time'].sum() / 1000 / 60
        idle_time_mins = lifetime_mins - running_time_mins
        idle_time_mins_ext = lifetime_mins_ext - running_time_mins
        
        list_of_vars = ['instance_id', 'lifetime_mins', 'lifetime_mins_ext', 'instance_start', 'instance_start_dt',
                       'instance_end', 'instance_end_ext', 'instance_end_dt', 'instance_end_ext_dt', 'running_time_mins',
                       'idle_time_mins', 'idle_time_mins_ext']
        all_instance_info.append(get_local_vars_as_dict(list_of_vars, locals()))
        
    df_inst = pd.DataFrame(data=all_instance_info)
    
    instance_end_times = list(df_inst['instance_end'].values)
    
    # add the is_last column (if a request is the last request container is serving)
    df.loc[:, 'is_last'] = df.apply(lambda x: x['client_end_time'] in instance_end_times, axis=1)
    
    list_of_vars = ['df', 'df_inst', ]
    return get_local_vars_as_dict(list_of_vars, locals())


def parse_counting_info(df, df_inst, step_seconds=10):
    time_instances_idx = pd.date_range(start=df['client_start_time_dt'].min(), end=df['client_start_time_dt'].max(), freq='{}S'.format(step_seconds))

    def func_instance_count(x):
        val = ((df_inst.loc[:,'instance_start_dt'] < x.name) & (df_inst.loc[:,'instance_end_ext_dt'] > x.name)).sum()
        if val is not None:
            return val
        else:
            return 0

    df_counts = pd.DataFrame(data = {'instance_count': 0}, index=time_instances_idx)
    df_counts['instance_count'] = df_counts.apply(func_instance_count, axis=1)

    # get running containers count
    def func_running_count(x):
        val = df.loc[(df.loc[:,'client_start_time_dt'] < x.name) & (df.loc[:,'client_end_time_dt'] > x.name), 'inst_id'].nunique()
        if val is not None:
            return val
        else:
            return 0

    # get running containers count
    def func_running_warm_count(x):
        val = df.loc[(df.loc[:,'client_start_time_dt'] < x.name) & (df.loc[:,'client_end_time_dt'] > x.name) & (df.loc[:,'is_cold'] == False), 'inst_id'].nunique()
        if val is not None:
            return val
        else:
            return 0

    df_counts['running_count'] = df_counts.apply(func_running_count, axis=1)
    df_counts['running_warm_count'] = df_counts.apply(func_running_warm_count, axis=1)
    df_counts['idle_count'] = df_counts['instance_count'] - df_counts['running_count']
    df_counts['utilization'] = df_counts['running_warm_count'] / df_counts['instance_count']

    df_counts.index = df_counts.index - df_counts.index.min()

    return df_counts
