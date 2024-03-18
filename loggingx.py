import logging
import os
import shutil
import sys
import zipfile
from io import StringIO
from logging.handlers import TimedRotatingFileHandler


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """
    自定义定时滚动日志处理器
    1、创建以天为单位的文件夹；
    2、日期作为文件名前缀；
    3、自定义日志存储路径；
    4、支持压缩；
    TODO: 修改文件命名后，会导致滚动删除失效，需要特殊处理；
    """

    def __init__(self, filename, when='h', interval=1,
                 encoding=None, delay=False, utc=False, atTime=None,
                 errors=None, log_dir=None, maxDay=7, compress=True):

        # 日志存储路径
        self.__log_dir = log_dir
        # 日志保存天数
        self.__max_day = maxDay
        # 是否压缩
        self.__compress = compress

        self.__check_dir(self.__log_dir)

        TimedRotatingFileHandler.__init__(self,
                                          filename=os.path.join(log_dir, filename),
                                          when=when,
                                          interval=interval,
                                          backupCount=0,
                                          encoding=encoding,
                                          delay=delay,
                                          utc=utc,
                                          atTime=atTime,
                                          errors=errors)

        def when_name(default_name: str):
            """
            日志文件重命名：'/Users/robin/IdeaProjects/demo/robin.log.2024-03-16_20-14'-> '/Users/robin/IdeaProjects/demo/logs/2024-03-16/robin_2024-03-16_21-06.log'
            :param default_name:
            :return:
            """
            dirname = os.path.dirname(self.baseFilename)
            basename = os.path.basename(self.baseFilename)
            filename, ext = os.path.splitext(basename)
            date_part = default_name.split('.')[2]
            date_str = date_part.split('_')[0]
            new_name = filename + \
                       "_" + \
                       date_part + \
                       ext
            new_dir = dirname + \
                      os.sep + \
                      date_str
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            return new_dir + os.sep + new_name

        def when_rotate(source, dest: str):
            """
            日志文件新建
            1、压缩日志；
            2、滚动删除，由于改变了目录结构，故原滚动机制时效，需在此实现；
            :param source:
            :param dest:
            :return:
            """
            if os.path.exists(source):

                # 1.重命名
                os.rename(source, dest)

                # 2.压缩文件
                if self.__compress:
                    basename = os.path.basename(source)
                    _, ext = os.path.splitext(basename)
                    zip_name = dest.replace(ext, '.zip')
                    # zip_name = dest.replace(ext, ext + '.zip')
                    try:
                        with zipfile.ZipFile(zip_name, 'w') as zipf:
                            zipf.write(dest, arcname=os.path.basename(dest))
                    except Exception as e:
                        raise e
                    if os.path.exists(dest):
                        os.remove(dest)

                # 3.滚动删除
                log_dir = os.path.dirname(os.path.dirname(dest))
                folder_paths = []
                for i in os.listdir(log_dir):
                    if os.path.isdir(os.path.join(log_dir, i)):
                        folder_paths.append(os.path.join(log_dir, i))
                if len(folder_paths) > self.__max_day:
                    folder_paths.sort()
                    to_delete = folder_paths[0:(len(folder_paths) - self.__max_day)]
                    # print(to_delete)
                    for expire in to_delete:
                        if os.path.exists(expire):
                            #  Too dangerous!!!
                            shutil.rmtree(expire)

        self.namer = when_name
        self.rotator = when_rotate

    def __check_dir(self, dir):
        if not os.path.exists(os.path.abspath(dir)):
            os.mkdir(dir)


class LoggingConfigurator(object):
    """
    logging配置
    功能：
    1、支持按天分目录保存，按小时分片；
    1、支持自定义日志名称；
    2、支持控制台、文件输入；
    3、支持运行时配置：leve、outputs；
    4、支持日志压缩；
    5、支持日志滚动删除：通过`maxDay`设置最大保留天数；
    TODO：
    1、日志文件按级分类保存：DEBUG、INFO...
    2、单个日志文件大小限制；
    """
    DEFAULT_LOG_FORMATE = "[%(asctime)s] [%(threadName)s] [%(filename)s:%(lineno)s] [%(levelname)s] %(message)s"
    STD_LOG_FORMATE = "%(message)s"

    # 全局参数
    global_log_prefix = None
    global_log_dir = None
    global_max_day = None
    global_logging_formatter = None
    global_std_log_formatter = None

    global_original_stdout = sys.stdout
    global_original_stderr = sys.stderr

    global_stream_handler = None
    global_logging_file_handler = None
    global_stdout_file_handler = None
    global_stderr_file_handler = None

    @staticmethod
    def setup(log_prefix="app",
              log_dir="logs",
              max_day=7,
              logging_formatter=DEFAULT_LOG_FORMATE,
              std_log_formatter=STD_LOG_FORMATE,
              log_outputs=('console', 'file', 'stdout', 'stderr'),
              log_level=logging.INFO):
        """
        初始化日志配置
        :param log_prefix: 日志文件名前缀
        :param log_path: 日志根目录
        :param logging_formatter: 日志格式化字符串
        :param log_outputs: 日志输出配置
            "console": logging打印日志输出到控制台；
            "file": logging打印日志保存至文件xxx.log；
            "stdout": print输出至文件xxx.stdout；
            "stderr": print输出至文件xxx.stderr；
        :return:
        """
        LoggingConfigurator.global_log_prefix = log_prefix
        LoggingConfigurator.global_log_dir = log_dir
        LoggingConfigurator.global_max_day = max_day
        LoggingConfigurator.global_logging_formatter = logging_formatter
        LoggingConfigurator.global_std_log_formatter = std_log_formatter

        LoggingConfigurator.global_original_stdout = sys.stdout
        LoggingConfigurator.global_original_stderr = sys.stderr

        LoggingConfigurator.reset("all")

        if "console" in log_outputs:
            LoggingConfigurator.__set_console_handler(log_level)
        if "file" in log_outputs:
            LoggingConfigurator.__set_logging_file_handler(log_level)
        if "stdout" in log_outputs:
            LoggingConfigurator.__set_stdout_file_handler(log_level)
        if "stderr" in log_outputs:
            LoggingConfigurator.__set_stderr_file_handler(log_level)

    @staticmethod
    def __set_console_handler(level):
        global_stream_handler = logging.StreamHandler()
        global_stream_handler.setFormatter(logging.Formatter(LoggingConfigurator.global_logging_formatter))
        root_logger = logging.getLogger()
        root_logger.addHandler(global_stream_handler)
        root_logger.setLevel(level)

    @staticmethod
    def __set_logging_file_handler(level):
        LoggingConfigurator.global_logging_file_handler = DailyRotatingFileHandler(
            filename=f"{LoggingConfigurator.global_log_prefix}.log",
            log_dir=LoggingConfigurator.global_log_dir,
            when='h',
            maxDay=LoggingConfigurator.global_max_day)
        LoggingConfigurator.global_logging_file_handler.setFormatter(
            logging.Formatter(LoggingConfigurator.global_logging_formatter))
        root_logger = logging.getLogger()
        root_logger.addHandler(LoggingConfigurator.global_logging_file_handler)
        root_logger.setLevel(level)

    @staticmethod
    def __set_stdout_file_handler(level):
        class Stdout2LoggingWrapper(StringIO):
            def write(self, message):
                LoggingConfigurator.global_original_stdout.write(message)
                stdout_logger.info(message)

        sys.stdout = Stdout2LoggingWrapper()
        LoggingConfigurator.global_stdout_file_handler = DailyRotatingFileHandler(
            filename=f"{LoggingConfigurator.global_log_prefix}.stdout",
            log_dir=LoggingConfigurator.global_log_dir,
            when='d',
            maxDay=LoggingConfigurator.global_max_day,
            compress=False)
        LoggingConfigurator.global_stdout_file_handler.setFormatter(
            logging.Formatter(LoggingConfigurator.global_std_log_formatter))
        stdout_logger = logging.getLogger("stdout")
        stdout_logger.propagate = False
        stdout_logger.addHandler(LoggingConfigurator.global_stdout_file_handler)
        stdout_logger.setLevel(level)

    @staticmethod
    def __set_stderr_file_handler(level):
        class Stderr2LoggingWrapper(StringIO):
            def write(self, message):
                LoggingConfigurator.global_original_stderr.write(message)
                stderr_logger.error(message)

        sys.stderr = Stderr2LoggingWrapper()
        LoggingConfigurator.global_stderr_file_handler = DailyRotatingFileHandler(
            filename=f"{LoggingConfigurator.global_log_prefix}.stderr",
            log_dir=LoggingConfigurator.global_log_dir,
            when='d',
            maxDay=LoggingConfigurator.global_max_day,
            compress=False)
        LoggingConfigurator.global_stderr_file_handler.setFormatter(
            logging.Formatter(LoggingConfigurator.global_std_log_formatter))
        stderr_logger = logging.getLogger("stderr")
        stderr_logger.propagate = False
        stderr_logger.addHandler(LoggingConfigurator.global_stderr_file_handler)
        stderr_logger.setLevel(level)

    @staticmethod
    def __reset_console_handler():
        root_logger = logging.getLogger()
        root_logger.removeHandler(LoggingConfigurator.global_stream_handler)

    @staticmethod
    def __reset_logging_file_handler():
        root_logger = logging.getLogger()
        root_logger.removeHandler(LoggingConfigurator.global_logging_file_handler)

    @staticmethod
    def __reset_stdout_file_handler():
        stdout_logger = logging.getLogger("stdout")
        stdout_logger.removeHandler(LoggingConfigurator.global_stdout_file_handler)
        stdout_logger.propagate = True
        sys.stdout = LoggingConfigurator.global_original_stdout

    @staticmethod
    def __reset_stderr_file_handler():
        stderr_logger = logging.getLogger("stderr")
        stderr_logger.removeHandler(LoggingConfigurator.global_stderr_file_handler)
        stderr_logger.propagate = True
        sys.stderr = LoggingConfigurator.global_original_stderr

    @staticmethod
    def reset(*args):
        if not args:
            raise ValueError("参数为空")
        if "console" in args:
            LoggingConfigurator.__reset_console_handler()
        if "file" in args:
            LoggingConfigurator.__reset_logging_file_handler()
        if "stdout" in args:
            LoggingConfigurator.__reset_stdout_file_handler()
        if "stderr" in args:
            LoggingConfigurator.__reset_stderr_file_handler()
        if "all" in args:
            LoggingConfigurator.__reset_console_handler()
            LoggingConfigurator.__reset_logging_file_handler()
            LoggingConfigurator.__reset_stdout_file_handler()
            LoggingConfigurator.__reset_stderr_file_handler()

    @staticmethod
    def set(*args, level):
        if not args:
            raise ValueError("参数为空")
        if "console" in args:
            LoggingConfigurator.__set_console_handler(level)
        if "file" in args:
            LoggingConfigurator.__set_logging_file_handler(level)
        if "stdout" in args:
            LoggingConfigurator.__set_stdout_file_handler(level)
        if "stderr" in args:
            LoggingConfigurator.__set_stderr_file_handler(level)
        if "all" in args:
            LoggingConfigurator.__set_console_handler(level)
            LoggingConfigurator.__set_logging_file_handler(level)
            LoggingConfigurator.__set_stdout_file_handler(level)
            LoggingConfigurator.__set_stderr_file_handler(level)
