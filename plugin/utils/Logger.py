import logging
from logging.handlers import TimedRotatingFileHandler

import time
import os
def make_dir(make_dir_path):
    path = make_dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path



def log_config():
    LOG_FORMAT = "[%(asctime)s][%(levelname)s]: %(message)s"
    fname = time.strftime("news_%Y%m%d.log", time.localtime())
    level = logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)

    # 创建TimedRotatingFileHandler对象,每天生成一个文件
    log_file_handler = TimedRotatingFileHandler(filename='test.log', when="D", interval=1, backupCount=3)
    # 设置日志打印格式
    formatter = logging.Formatter(LOG_FORMAT)
    log_file_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(log_file_handler)


def create_logger(loglevel:str):
    project_name = "log"
    folder_format = time.strftime('%Y-%m', time.localtime(time.time()))
    log_file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    log_file_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) + os.sep + project_name + os.sep + folder_format
    make_dir(log_file_folder)
    log_file_str = log_file_folder + os.sep + log_file_name

    logger = logging.getLogger()
    loglevel = loglevel.upper()
    if loglevel in ["CRITICAL","FATAL"]:
        loggerlevel = logging.CRITICAL
    elif loglevel == "ERROR":
        loggerlevel = logging.ERROR
    elif loglevel == "INFO":
        loggerlevel = logging.INFO
    elif loglevel in ["WARNING","WARN"]:
        loggerlevel = logging.WARNING
    else:
        loggerlevel = logging.DEBUG
    logger.setLevel(loggerlevel)
    logger_format = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    timerhandler = TimedRotatingFileHandler(filename=log_file_str, when="D", interval=1,backupCount=0,encoding='utf-8')
    timerhandler.setFormatter(logger_format)

    logger.addHandler(timerhandler)

    return logger

def getQQlogger():

    project_name = "qq-log"
    folder_format = time.strftime('%Y-%m', time.localtime(time.time()))
    log_file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    log_file_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) + os.sep + project_name + os.sep + folder_format
    make_dir(log_file_folder)
    log_file_str = log_file_folder + os.sep + log_file_name

    logger = logging.getLogger("qqlogger")
    logger.setLevel(20)
    logger_format = logging.Formatter(fmt='time="%(asctime)s" - level=%(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    timerhandler = TimedRotatingFileHandler(filename=log_file_str, when="D", interval=1,backupCount=0,encoding='utf-8')
    timerhandler.setFormatter(logger_format)

    logger.addHandler(timerhandler)

    return logger