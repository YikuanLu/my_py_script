import os
import time
import datetime
import sys
import socket
import shutil
import logging

logging.basicConfig(level=logging.INFO)

dbconfig = {
    'host': '127.0.0.1',
    'port': '3306',
    'user': 'root',
    'password': 'qwer',
    'database': 'test_DB',
}

# 存放备份文件的目录
backup_dir = F"{os.path.expandvars('$HOME')}/fish/db/backup"
backupfilelist = os.path.join(backup_dir, "backupfilelist.log")
backup_keep_days = 15  # 保存几天的备份数据


# 全量备份
def full_backup(backup_file_name):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 执行全量备份语句
    backup_commond = F'mysqldump -u{dbconfig["user"]} -p{dbconfig["password"]} --quick -E --lock-tables -F --databases {dbconfig["database"]} > {backup_dir}/{backup_file_name}.sql'
    execute_result = os.system(backup_commond)
    return execute_result


# 增量备份
def incr_backup(backup_file_name):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_commond = F'mysqladmin -u {dbconfig["user"]} -p{dbconfig["password"]} flush-logs'
    execute_result = os.system(backup_commond)
    return execute_result


# 获取备份类型，周六进行完备，平时增量备份，如果没有全备，执行完整备份
def get_backup_type():
    backup_type = None
    if os.path.exists(backupfilelist):
        with open(backupfilelist, 'r') as f:
            lines = f.readlines()
            if (lines):
                last_line = lines[-1]  # get last backup name
                if (last_line):
                    if (time.localtime().tm_wday == 6):
                        backup_type = "full"
                    else:
                        backup_type = "incr"
                else:
                    backup_type = "full"
            else:
                backup_type = "full"
    else:
        open(backupfilelist, "a").close()
        backup_type = "full"
    return backup_type


# 探测实例端口号
def get_mysqlservice_status():
    mysql_stat = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((dbconfig['host'], int(dbconfig['port'])))
    # port os open
    if (result == 0):
        mysql_stat = 1
    return mysql_stat


if __name__ == '__main__':
    mysql_stat = get_mysqlservice_status()
    if mysql_stat <= 0:
        logging.warning("😱 mysql instance is inactive,backup exit")
        sys.exit(1)

    try:
        backup_type = get_backup_type()
        start_backup_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(F"{start_backup_time}--------start backup")
        start_time = datetime.datetime.now().strftime('%Y%m%d%_H%M%S')
        backup_file_name = start_time
        execute_result = None
        if (backup_type == "full"):
            backup_file_name = F"{backup_file_name}_full"
            logging.info("execute full backup......")
            execute_result = full_backup(backup_file_name)
            if (execute_result == 0):
                logging.info(
                    F"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}--------begin cleanup history backup")
                logging.info("execute cleanup backup history......")
                logging.info(
                    F"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}--------finsh cleanup history backup")
        else:
            backup_file_name = F"{backup_file_name}_incr"
            logging.info("execute incr backup......")
            execute_result = incr_backup(backup_file_name)

        if(execute_result == 0):
            finish_time = datetime.datetime.now().strftime('%Y%m%d%_H%M%S')
            backup_info = F'{start_time}|{finish_time}|{start_time}_{backup_type}'
            with open(backupfilelist, 'a+') as f:
                f.write(backup_info + '\n')
            logging.info(datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')+"--------finish backup")
        else:
            logging.info(datetime.datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S') + "--------xtrabackup failed.please check log")

    except:
        raise
        sys.exit(1)
