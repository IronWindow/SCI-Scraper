import os

import pandas as pd


def find_row():
    row_num = 0
    output_file_exists = os.path.isfile('output.csv')
    doi_list_exists = os.path.isfile('doi_list_rev.csv')
    if output_file_exists:
        # 读取整个 CSV 文件,output有表头
        df = pd.read_csv('output.csv')
        # 获取最后一行
        last_row = df.iloc[-1, 0]
        # 打印或处理最后一行数据
        print("last_row:", last_row)
        if doi_list_exists:
            # 读取整个 CSV 文件
            df = pd.read_csv('doi_list_rev.csv')
            processed_row = df[df['DOI'] == last_row]
            row_num = processed_row.index
            print("processed:", processed_row)
            # print("row_num:", row_num)
        else:
            print("No 'doi_list_rev.csv', or need rename")
    else:
        print("No 'output.csv', or need rename")
    return row_num.tolist()[0] + 2


if __name__ == "__main__":
    a = find_row()
    print("type:", type(a), a)
