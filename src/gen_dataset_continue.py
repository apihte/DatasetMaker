import os
import json
from datetime import datetime
import utils


# 获取资源目录路径
log_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
logger = utils.setup_logger(log_directory, 'gen_dataset_continue')


def generate_dataset(folder_path, input_size, output_size, instruction):
    try:
        # 存储所有问答对的列表
        dataset = []

        # 检查并重命名已存在的 dataset.json 文件
        existing_dataset_path = os.path.join(folder_path, 'dataset.json')
        if os.path.exists(existing_dataset_path):
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            new_filename = f'dataset-{timestamp}.json'
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(existing_dataset_path, new_filepath)
            logger.info(f"Renamed existing dataset.json to {new_filepath}")

        # 遍历 folderPath 及其子文件夹中的所有 txt 文件
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(".txt"):
                    file_path = os.path.join(root, filename)

                    lines, encoding = utils.read_file_with_encoding(file_path)
                    if lines is None:
                        continue

                    if encoding != "utf-8":
                        logger.error(f"Read {file_path} using encoding: {encoding}")
                        continue

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
                        if len(accumulated_content) > input_size + output_size:
                            # 处理只有一行文本的情况
                            if len(lines) == 1 or start_line_index == 0:
                                split_pos = utils.find_split_position(accumulated_content.strip(), input_size)
                                input_content = accumulated_content[:split_pos].strip()
                                output_content = accumulated_content[split_pos:].strip()
                            else:
                                # 处理多行文本的情况
                                split_pos = utils.find_split_return(accumulated_content.strip(), input_size)
                                input_content = accumulated_content[:split_pos].strip()
                                output_content = accumulated_content[split_pos:].strip()

                            # 创建问答对
                            qa_pair = {
                                "instruction": instruction,
                                "input": input_content,
                                "output": output_content
                            }

                            # 添加到数据集中
                            dataset.append(qa_pair)

                            # 重置累积内容
                            accumulated_content = ""

                        start_line_index += 1

        # 将数据集写入 dataset.json 文件
        dataset_file_path = os.path.join(folder_path, 'dataset.json')
        with open(dataset_file_path, 'w', encoding='utf-8') as dataset_file:
            json.dump(dataset, dataset_file, ensure_ascii=False, indent=4)

        logger.info(f"Generated {len(dataset)} QA pairs and saved to {dataset_file_path}")

    except Exception as e:
        logger.error(f"Error generating dataset: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        logger.error("Usage: python gen_dataset_continue.py <folderPath> <inputSize> <outputSize> <instruction>")
        sys.exit(1)

    folderPath = sys.argv[1]
    inputSize = int(sys.argv[2])
    outputSize = int(sys.argv[3])
    instrContent = sys.argv[4]

    generate_dataset(folderPath, inputSize, outputSize, instrContent)
