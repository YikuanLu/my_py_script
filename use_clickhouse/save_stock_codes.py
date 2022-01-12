# from datetime import datetime
import numpy as np
import csv
from my_config import ClickhouseConfig
import time


def save_stock_codes(get_day_time, url='files/stock_codes.csv'):
    use_config = ClickhouseConfig()
    client = use_config.create_client()

    sql = "SELECT DISTINCT instrument FROM TICK_{0} t".format(get_day_time)
    clickhouse_list = client.execute(sql)

    ls = np.array(clickhouse_list)
    ls.flatten('C')

    with open(url, 'w') as f:
        writer = csv.writer(f)
        csv.writer(f)
        writer.writerows(ls)


today_time = time.strftime("%Y%m%d", time.localtime())
save_stock_codes(today_time)
print('写入成功')
