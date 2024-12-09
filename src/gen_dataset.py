import os
import json
from datetime import datetime
import logging
import string


# 设置日志配置
def setup_logger(log_dir):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, 'gen_dataset.log')

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

logger = setup_logger(log_directory)


def find_split_position(line, inputSize):
    # 找到 inputSize 长度的位置
    end_index = inputSize

    # 向后寻找最近的一个标点符号
    punctuation_set = set(string.punctuation + "，。！？；：")
    for i in range(end_index, len(line)):
        if line[i] in punctuation_set:
            return i + 1  # 返回标点符号后面的位置

    # 如果没有找到标点符号，则返回 inputSize 长度的位置
    return end_index


def find_split_return(line, inputSize):
    # 找到 inputSize 长度的位置
    end_index = inputSize

    # 向后寻找最近的一个标点符号
    punctuation_set = set(string.whitespace)
    for i in range(end_index, len(line)):
        if line[i] in punctuation_set:
            return i + 1  # 返回标点符号后面的位置

    # 如果没有找到标点符号，则返回 inputSize 长度的位置
    return end_index


def generate_dataset(folderPath, inputSize, outputSize, instruction):
    try:
        # 存储所有问答对的列表
        dataset = []

        # 检查并重命名已存在的 dataset.json 文件
        existing_dataset_path = os.path.join(folderPath, 'dataset.json')
        if os.path.exists(existing_dataset_path):
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            new_filename = f'dataset-{timestamp}.json'
            new_filepath = os.path.join(folderPath, new_filename)
            os.rename(existing_dataset_path, new_filepath)
            logger.info(f"Renamed existing dataset.json to {new_filepath}")

        # 遍历 folderPath 中的所有 txt 文件
        for filename in os.listdir(folderPath):
            if filename.endswith(".txt"):
                file_path = os.path.join(folderPath, filename)

                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                    # 初始化索引和内容累积变量
                    start_line_index = 0
                    accumulated_content = ""

                    while start_line_index < len(lines):
                        line = lines[start_line_index].strip()

                        # 跳过空白行
                        if not line:
                            start_line_index += 1
                            continue

                        # 累积内容
                        accumulated_content += (line + "\n").strip() + "\n"

                        # 检查累积内容长度是否超过 inputSize + outputSize
                        if len(accumulated_content) > inputSize + outputSize:
                            # 处理只有一行文本的情况
                            if len(lines) == 1 or start_line_index == 0:
                                split_pos = find_split_position(accumulated_content.strip(), inputSize)
                                inputContent = accumulated_content[:split_pos].strip()
                                outputContent = accumulated_content[split_pos:].strip()
                            else:
                                # 处理多行文本的情况
                                split_pos = find_split_return(accumulated_content.strip(), inputSize)
                                inputContent = accumulated_content[:split_pos].strip()
                                outputContent = accumulated_content[split_pos:].strip()

                            # 创建问答对
                            qa_pair = {
                                "instruction": instruction,
                                "input": inputContent,
                                "output": outputContent
                            }

                            # 添加到数据集中
                            dataset.append(qa_pair)

                            # 重置累积内容
                            accumulated_content = ""

                        start_line_index += 1

        # 将数据集写入 dataset.json 文件
        dataset_file_path = os.path.join(folderPath, 'dataset.json')
        with open(dataset_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(dataset, outfile, ensure_ascii=False, indent=4)

        logger.info(f"Generated {len(dataset)} QA pairs and saved to {dataset_file_path}")

    except Exception as e:
        logger.error(f"Error generating dataset: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        logger.error("Usage: python gen_dataset.py <folderPath> <inputSize> <outputSize> <instruction>")
        sys.exit(1)

    folderPath = sys.argv[1]
    inputSize = int(sys.argv[2])
    outputSize = int(sys.argv[3])
    instruction = sys.argv[4]

    generate_dataset(folderPath, inputSize, outputSize, instruction)



