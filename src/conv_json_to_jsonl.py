import json
import os
from datetime import datetime
import logging


# 设置日志配置
def setup_logger(log_dir):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, 'conv_json_to_jsonl.log')

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


def convert_json_to_jsonl(input_file_path, output_file_path):
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file {input_file_path} does not exist.")

        # 检查输出文件是否存在，如果存在则重命名
        if os.path.exists(output_file_path):
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            new_filename = f'dataset-{timestamp}.jsonl'
            new_filepath = os.path.join(os.path.dirname(output_file_path), new_filename)
            os.rename(output_file_path, new_filepath)
            logger.info(f"Renamed existing dataset.jsonl to {new_filepath}")

        # 读取 input_file_path 中的 JSON 数据
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            dataset = json.load(infile)

        # 写入 output_file_path 作为 JSONL 格式
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            for item in dataset:
                json.dump(item, outfile, ensure_ascii=False)
                outfile.write('\n')

        logger.info(f"Converted {len(dataset)} records from {input_file_path} to {output_file_path}")

    except Exception as e:
        logger.error(f"Conversion to JSONL failed: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        logger.error("Usage: python convert_json_to_jsonl.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    logger.info(f"Convert dataset from {input_file_path} to {output_file_path}")

    convert_json_to_jsonl(input_file_path, output_file_path)

