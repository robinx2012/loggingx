import logging
import sys
import threading
from time import sleep

from loggingx import LoggingConfigurator

if __name__ == "__main__":
    # LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
    #                           log_outputs=("console", "file", "stdout", "stderr"))
    LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
                              log_outputs=("console"))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)


    # 测试 log level
    # logger.setLevel(logging.DEBUG)
    # logger.debug("before...")
    # logger.setLevel(lxogging.INFO)
    # logger.debug("after...")
    #
    # logger.setLevel(logging.INFO)
    # logger.info("before...")
    # logger.setLevel(logging.DEBUG)
    # logger.info("after...")

    def run():
        sleep(10)
        LoggingConfigurator.set("file", level=logging.DEBUG)
        LoggingConfigurator.set("stderr", level=logging.DEBUG)
        LoggingConfigurator.set("stdout", level=logging.DEBUG)
        sleep(10)
        LoggingConfigurator.reset("file")
        LoggingConfigurator.reset("stderr")
        LoggingConfigurator.reset("stdout")
        sleep(10)
        LoggingConfigurator.set("file", level=logging.DEBUG)
        LoggingConfigurator.set("stderr", level=logging.DEBUG)
        LoggingConfigurator.set("stdout", level=logging.DEBUG)


    t = threading.Thread(target=run)
    t.start()

    while True:
        sleep(0.8)
        logger.log(logging.WARNING, "God bless you:logging")
        print("God bless you: stdout", file=sys.stdout)
        print("God bless you: stderr", file=sys.stderr)
