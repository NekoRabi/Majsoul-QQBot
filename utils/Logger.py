import logging
from logging.handlers import TimedRotatingFileHandler
from utils.cfg_loader import read_file

import time
import os

__all__ = ['root_logger', 'create_logger']


def make_dir(make_dir_path):
    path = make_dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


_cfg = read_file(r'./config/config.yml')


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


def create_logger(log_level: str = 'INFO', logger_name: str = None, log_file_folder: str = r'./log',
                  fmt='%(asctime)s - %(name)s - %(levelname)-6s  - %(message)s', date_fmt='%Y-%m-%d %H:%M:%S',
                  timer_config=None):
    """
    创建Logger

    Args:
        log_level: 日志等级
        logger_name: Logger_Name,默认root
        log_file_folder: 日志存储路径
        fmt: 日志输出格式
        date_fmt: 时间格式
        timer_config: Timer配置

    Returns:Logger

    """
    if timer_config is None:
        timer_config = dict(when="D", interval=1, backupCount=0)
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()
    loglevel = log_level.upper()
    if loglevel in ["CRITICAL", "FATAL"]:
        loggerlevel = logging.CRITICAL
    elif loglevel == "ERROR":
        loggerlevel = logging.ERROR
    elif loglevel == "INFO":
        loggerlevel = logging.INFO
    elif loglevel in ["WARNING", "WARN"]:
        loggerlevel = logging.WARNING
    else:
        loggerlevel = logging.DEBUG
    logger.setLevel(loggerlevel)
    # logger_format = logging.Formatter(
    #     fmt='%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s',
    #     datefmt='%Y-%m-%d %H:%M:%S')
    logger_format = logging.Formatter(
        fmt=fmt,
        datefmt=date_fmt)

    timerhandler = TimedRotatingFileHandler(filename=_get_rootlog_filename(log_file_folder),
                                            when=timer_config.get('when', 'D'),
                                            interval=timer_config.get('interval', 1),
                                            backupCount=timer_config.get('backupCount', 0),
                                            encoding='utf-8')
    timerhandler.setFormatter(logger_format)

    logger.addHandler(timerhandler)

    return logger


def _get_rootlog_filename(log_file_folder):
    """自动生成日志文件名"""
    #     project_name = "log"
    folder_format = time.strftime('%Y-%m', time.localtime(time.time()))
    log_file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    # log_file_folder = os.path.abspath(
    #     os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) + os.sep + project_name + os.sep + folder_format
    make_dir(log_file_folder)
    log_file_str = log_file_folder + os.sep + log_file_name
    return log_file_str


# def getQQlogger():
#     """已弃用的聊天记录日志记录器"""
#     project_name = "qq-log"
#     # log_file_folder = os.path.abspath(
#     #     os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) + os.sep + project_name + os.sep + folder_format
#
#     log_file_folder = r'./qq-log'
#     make_dir(log_file_folder)
#     folder_format = time.strftime('%Y-%m', time.localtime(time.time()))
#     log_file_name = time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
#     log_file_str = log_file_folder + os.sep + log_file_name
#     logger = logging.getLogger("qqlogger")
#     logger.setLevel(20)
#     logger_format = logging.Formatter(fmt='time="%(asctime)s" - level=%(levelname)s - %(message)s',
#                                       datefmt='%Y-%m-%d %H:%M:%S')
#
#     timerhandler = TimedRotatingFileHandler(filename=log_file_str, when="D", interval=1, backupCount=1,
#                                             encoding='utf-8')
#     timerhandler.setFormatter(logger_format)
#
#     logger.addHandler(timerhandler)
#
#     return logger


root_logger = create_logger(_cfg.get('loglevel', 'INFO'))
# QQ_logger = getQQlogger()
# 每隔 1000 Byte 划分一个日志文件，备份文件为 3 个
