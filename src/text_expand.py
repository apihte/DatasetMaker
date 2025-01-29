import os
import utils
from datetime import datetime


# 获取资源目录路径
log_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
logger = utils.setup_logger(log_directory, 'text_expand')


def expand(folder_path, file_name, prev_content):
    output_file_name = 'expanded.txt'

    source_file_path = os.path.join(folder_path, file_name)

    existing_file_path = os.path.join(folder_path, output_file_name)
    if os.path.exists(existing_file_path):
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        new_filename = f'{output_file_name}-{timestamp}'
        new_filepath = os.path.join(folder_path, new_filename)
        os.rename(existing_file_path, new_filepath)
        logger.info(f"Renamed existing file to {new_filepath}")

    # 读取txt文件并处理每行内容
    with open(source_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 处理每行内容并在前面加入特定内容
    processed_lines = [f'{prev_content}:"{line.strip()}"\n' for line in lines]

    # 写入处理后的内容到新的txt文件
    with open(existing_file_path, 'w', encoding='utf-8') as file:
        file.writelines(processed_lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        logger.error("Usage: python text_expand.py <text_file> <prev_content>")
        sys.exit(1)

    folderPath = sys.argv[1]
    textFileName = sys.argv[2]
    prev = sys.argv[3]

    expand(folderPath, textFileName, prev)

