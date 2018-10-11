import logging
from logging import handlers

# 日志级别字典
__level_dict = {
    'critical': logging.CRITICAL,
    'fatal': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


def getLogger(filename, level='info', when='D', backupCount=3,
              fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
    """
    获取日志处理对象

    :param filename: 日志文件名称
    :param level: 日志等级：debug, info, warn/warning, error, critical
    :param when: 日志文件分割的时间单位，单位有以下几种:<br>
                - S 秒<br>
                - M 分<br>
                - H 小时<br>
                - D 天<br>
                - W 每星期<br>
                - midnight 每天凌晨<br>
    :param backupCount: 备份文件的个数，如果超过这个数量，就会自动删除
    :param fmt: 日志信息格式
    :return:
    """
    level = __level_dict.get(level.lower(), None)
    logger = logging.getLogger(filename)
    # 设置日志格式
    format_str = logging.Formatter(fmt)
    # 设置日志级别
    logger.setLevel(level)
    # 控制台输出
    console_handler = logging.StreamHandler()
    # 控制台输出的格式
    console_handler.setFormatter(format_str)
    logger.addHandler(console_handler)

    # 文件输出
    file_handler = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backupCount,
                                                     encoding='utf-8')

    # 文件输出的格式
    file_handler.setFormatter(format_str)  # 设置写入文件的格式
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':
    log = getLogger('test.log')
    log.debug('debug')
    log.info('info')
    log.warning('警告')
    log.error('报错')
    log.critical('严重')
    getLogger('error.log', level='error').error('error')
