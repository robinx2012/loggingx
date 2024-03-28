# Overview

A non-intrusive, out-of-the-box, comprehensive, and flexible configuration tool class based on logging, which supports
logging to console, file saving, redirecting stderr, stdout, daily folder splitting, and zip compression.

# Feature

1. 支持按天分目录保存，按小时分片；
2. 支持自定义日志名称；
3. 支持控制台、文件输出；
4. 支持运行时配置：level、outputs；
5. 支持日志压缩；
6. 支持日志滚动删除：通过`maxDay`设置最大保留天数；
7. 支持`stdout`、`stderr`文件保存；

# Usage：

```python
"""
初始化日志配置
:param log_prefix: 日志文件名前缀
:param log_path: 日志根目录
:param logging_formatter: 日志格式化字符串
:param log_outputs: 日志输出配置
    "logging_console":  logging打印日志输出到控制台；
    "logging_file":     logging打印日志保存至文件xxx.log；
    "std_console":      print打印日志输出到控制台；
    "std_file":         print输出至文件xxx.stdout或xxx.stderr；
:return:
"""
LoggingConfigurator.setup(log_prefix="robin", log_dir="logs", max_day=5,
                          log_outputs=(
                              "logging_console",
                              "logging_file",
                              "std_console",
                              "std_file",
                          ))
```

# TODO:

1. 单个日志文件大小限制；
2. 日志文件总大小限制；