import os
import logging
import string


# 设置日志配置
def setup_logger(log_dir, file_name):
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)

    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, file_name + '.log')

    # 确保 log_file_path 是字符串
    if isinstance(log_file_path, bytes):
        log_file_path = log_file_path.decode('utf-8')

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 将格式化器添加到处理器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 获取资源目录路径
log_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
logger = setup_logger(log_directory, 'utils')


def find_split_position(line, content_size):
    # 找到 inputSize 长度的位置
    end_index = content_size

    # 从 content_size 开始向前寻找最近的一个标点符号
    punctuation_set = set(string.punctuation + "」』]”。！？")
    for i in range(content_size - 1, -1, -1):
        if line[i] in punctuation_set:
            return i + 1  # 返回标点符号后面的位置

    # 如果没有找到标点符号，则返回 inputSize 长度的位置
    return end_index


def find_split_return(accumulated_content, content_size):
    # 找到 inputSize 长度的位置
    end_index = content_size

    # 从 content_size 开始向前寻找最近的一个换行符
    for i in range(content_size - 1, -1, -1):
        if accumulated_content[i] == '\n':
            return i + 1  # 返回换行符后面的位置

    # 如果没有找到换行符，则返回 inputSize 长度的位置
    return end_index


def read_file_with_encoding(file_path, encodings=None):
    if encodings is None:
        encodings = ['utf-8', 'latin1', 'cp1252', 'gb2312', 'gbk', 'gb18030', 'big5', 'shift_jis',
                     'euc_kr', 'iso-8859-1', 'iso-8859-2', 'iso-8859-3', 'iso-8859-4', 'iso-8859-5',
                     'iso-8859-6', 'iso-8859-7', 'iso-8859-8', 'iso-8859-9', 'iso-8859-10',
                     'iso-8859-11', 'iso-8859-13', 'iso-8859-14', 'iso-8859-15', 'iso-8859-16']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.readlines(), encoding
        except UnicodeDecodeError:
            continue
    logger.error(f"Failed to decode {file_path} with any of the encodings: {encodings}")
    return None, None


def remove_invalid_content(text, invalid_contents=None):
    if invalid_contents is None:
        invalid_contents = [
            "＊＊＊",
            "#"
        ]
    for content in invalid_contents:
        text = text.replace(content, "")
    return text
