import logging

from loggingx import LoggingConfigurator

if __name__ == "__main__":
    #  console
    # LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
    #                           log_outputs=(
    #                               "logging_console",
    #                               "std_console",
    #                           ))

    # file
    # LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
    #                           log_outputs=(
    #                               "logging_file",
    #                               "std_file",
    #                           ))
    #
    # logging
    # LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
    #                           log_outputs=(
    #                               "logging_console",
    #                               "logging_file",
    #                           ))
    #
    # std
    # LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
    #                           log_outputs=(
    #                               "std_console",
    #                               "std_file",
    #                           ))

    # all
    LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
                              log_outputs=(
                                  "logging_console",
                                  "logging_file",
                                  "std_console",
                                  "std_file",
                              ))

    # output
    logging.info("logging.info(): 1")
    logging.info("logging.info(): 2")
    print("print(): 1")
    print("print(): 2")
    0 / 0
