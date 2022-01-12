# -m 模拟数据url，-r 实盘数据url
import numpy as np
import pandas as pd
import time
from datetime import datetime
import logging
import sys
import getopt


logging.basicConfig(level=logging.INFO)


# 获取参数
def get_argv():
    real_url = None
    simulation_url = None
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "m:r:")  # 短选项模式

    except:
        print("Error")

    for opt, arg in opts:
        if opt in ['-m']:
            simulation_url = arg
        elif opt in ['-r']:
            real_url = arg

    if(real_url == None or simulation_url == None):
        logging.error('参数错误')
        return
    return real_url, simulation_url


# 去除空格和换行符
def strip_str(str):
    return str.strip("\n")


# 时间转换为毫秒时间戳
def get_time(timestr):
    datetime_obj = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
    obj_stamp = int(time.mktime(datetime_obj.timetuple()) *
                    1000.0 + datetime_obj.microsecond / 1000.0)
    return obj_stamp


# 数据清洗
def data_cleaning(url):
    with open(url, 'r') as f:
        logs = np.array(f.readlines())
        orders = filter(lambda x: ' Order:' in x, logs)
        duty_ls = np.array(list(orders))
        clear_str = np.array(list(map(strip_str, duty_ls)))
        str_ls = np.array(list(map(lambda x: x[x.find('Order:'):], clear_str)))
        result = np.array(list(map(lambda x: x.split(','), str_ls)))
        pd_data = pd.DataFrame(result)
        pd_data[2] = pd_data[2].apply(lambda x: x.strip())
        pd_data[0] = pd_data[0].apply(
            lambda x: x[x.find(':')+1:].strip()) + '-' + pd_data[2]
        pd_data[6] = pd_data[6].apply(lambda x: x.strip())
        pd_data[7] = pd_data[6].apply(get_time)
        # print('pd_data', pd_data)
        pd_data = pd_data.sort_values(by=[2, 6])  # 排序数据
        groups = pd_data.groupby(2)  # 根据某列分组
        keys = list(groups.groups.keys())  # 获取所有组的keys
        # print(groups.get_group(keys[2]))  # 获取某组数据
        drop_duplicates_data = pd_data.drop_duplicates(subset=0)
        return keys, drop_duplicates_data


def create_result_data(simulation_data, real_data):
    is_eq = simulation_data[0].equals(real_data[0])
    if (is_eq == False):
        print('数据不一致')
        return
    result_df = pd.DataFrame()
    result_df['股票代码'] = simulation_data[2]
    result_df['方向'] = simulation_data[0].apply(
        lambda x: x[:x.find('-')])
    result_df['模拟时间'] = simulation_data[6]
    result_df['实盘时间'] = real_data[6]
    time_diff_key = '实盘比模拟盘快的时间(毫秒)'
    result_df[time_diff_key] = real_data[7] - simulation_data[7]
    result_df['模拟报价'] = simulation_data[4]
    result_df['模拟手数'] = simulation_data[3]
    result_df['实盘报价'] = real_data[4]
    result_df['实盘手数'] = real_data[3]
    return result_df


if __name__ == "__main__":
    real_url, simulation_url = get_argv()
    real_keys, real_pd_data = data_cleaning(real_url)
    simulation_keys, simulation_pd_data = data_cleaning(simulation_url)

    same_codes = set(real_keys) & set(simulation_keys)

    to_use_real_data = real_pd_data.loc[real_pd_data[2].isin(same_codes)]
    to_use_simulation_data = simulation_pd_data.loc[simulation_pd_data[2].isin(
        same_codes)]  # 模拟

    same_use_data = set(to_use_real_data[0]) & set(to_use_simulation_data[0])
    to_use_simulation_data = to_use_simulation_data.loc[to_use_simulation_data[0].isin(
        same_use_data)]
    to_use_simulation_data.index = range(len(to_use_simulation_data))

    to_use_real_data = to_use_real_data.loc[to_use_real_data[0].isin(
        same_use_data)]
    to_use_real_data.index = range(len(to_use_real_data))

    result_df = create_result_data(to_use_simulation_data, to_use_real_data)

    logging.info(F'模拟盘多做:{set(simulation_keys)-set(real_keys)}')
    logging.info(F'实盘多做:{set(real_keys)-set(simulation_keys)}')
    logging.info(result_df)
    result_df.to_csv('result.csv')
