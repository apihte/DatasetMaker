import os
import utils
from datetime import datetime


# 获取资源目录路径
log_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources'))
logger = utils.setup_logger(log_directory, 'split_text')


def split(folder_path, segment_size, output_file_name):
    try:
        # 存储所有问答对的列表
        result_list = []

        # 检查并重命名已存在的输出文件
        existing_dataset_path = os.path.join(folder_path, output_file_name)
        if os.path.exists(existing_dataset_path):
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            new_filename = f'{output_file_name}-{timestamp}'
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(existing_dataset_path, new_filepath)
            logger.info(f"Renamed existing file to {new_filepath}")

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

                        # 检查累积内容长度是否超过 segment_size
                        if len(accumulated_content) > segment_size:
                            # 处理只有一行文本的情况
                            if len(lines) == 1 or start_line_index == 0:
                                split_pos = utils.find_split_position(accumulated_content.strip(), segment_size)
                                segment_content = accumulated_content[:split_pos].strip()
                                left_content = accumulated_content[split_pos:].strip()
                            else:
                                # 处理多行文本的情况
                                split_pos = utils.find_split_return(accumulated_content.strip(), segment_size)
                                segment_content = accumulated_content[:split_pos].strip()
                                left_content = accumulated_content[split_pos:].strip()

                            # 添加到数据集中
                            result_list.append(segment_content)

                            # 重置累积内容
                            accumulated_content = left_content

                        start_line_index += 1

        # 将数据集写入结果文件
        output_file_path = os.path.join(folder_path, output_file_name)
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for line in result_list:
                output_file.write(line.replace('\n', '\\n'))  # 将 \n 替换为 \\n
                output_file.write('\n')  # 每个元素后添加一个换行符

        logger.info(f"Generated {len(result_list)} segments and saved to {output_file_path}")

    except Exception as e:
        logger.error(f"Error generating dataset: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        logger.error("Usage: python split_text.py <folderPath> <segmentSize> <outputFile>")
        sys.exit(1)

    folderPath = sys.argv[1]
    inputSize = int(sys.argv[2])
    outputFile = sys.argv[3]

    split(folderPath, inputSize, outputFile)
