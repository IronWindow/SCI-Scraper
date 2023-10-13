import csv
import os
import re
import time
import pandas as pd
import requests
from requests import exceptions

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scihub3.find_row import find_row


def download_pdf(pdf_url, doi):
    # PDF文件的URL
    # pdf_url = "location.href='//zero.sci-hub.se/4371/2aa19134c17c5c3fe37bd124cd2b7eec/jorne1982.pdf?download=true'"
    # pdf_url = "location.href='/downloads/2019-01-23//76/zhang2014.pdf?download=true'"
    # doi = "10.1149/1.2124051"
    # 发送HTTP GET请求并获取响应
    doi = doi.split('/', 1)[1]
    start_index = pdf_url.find("'//")
    if start_index != -1:
        # 提取 "//" 后的部分
        extracted_part = pdf_url[start_index+1:]
        pdf_url = "https:"+extracted_part
        print("true pdf:", pdf_url)
    max_retries = 3
    for retry in range(max_retries):
        try:
            response = requests.get(pdf_url)
            time.sleep(5)
            # 检查响应状态
            if response.status_code == 200:
                save_path = "downloads"
                # 检查路径是否存在，如果不存在则创建
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                # 合成完整的文件路径
                file_name = os.path.join(save_path, doi.replace('/', '+') .replace(':', '-').replace('<', '[').replace('>', ']') + ".pdf")
                # file_name = doi.replace('/', '+')+".pdf"
                # print(response.content)
                # print(file_name)
                # 保存PDF内容到本地文件
                with open(file_name, "wb") as pdf_file:
                    pdf_file.write(response.content)
                print("PDF文件下载成功")
                return 1
            else:
                print("无法下载PDF文件，HTTP响应状态码：", response.status_code)
                return 0
        except exceptions.SSLError:
            print("meet SSLError, going to try again")


def find_pdf_Link(doi_url):
    # option = webdriver.ChromeOptions()
    # option.add_experimental_option("detach", True)

    driver = webdriver.Chrome()
    # 设置最大重试次数和超时时间
    # 在循环中执行操作，最多重试max_retries次
    pdf_Link = ""
    max_retries = 3
    doi = re.search(r'http://(.+)', doi_url).group(1)

    scihub_doi = "https://sci-hub.se/" + doi_url
    for retry in range(max_retries):
        try:
            driver.get(scihub_doi)
            # 设置隐式等待
            driver.implicitly_wait(10)

            attempts = 0
            while attempts < 2:
                try:
                    flag_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'logo'))
                    )
                    print("loaded")
                    break
                except StaleElementReferenceException:
                    attempts += 1
                    print(attempts, "times meet StaleElementReferenceException")
                    time.sleep(5)
                    driver.get(scihub_doi)
                except NoSuchElementException:
                    attempts += 1
                    print(attempts, "times meet NoSuchElementException, Maybe meet Special Page")
            exam_flag = driver.find_elements(By.ID, "smile")
            # print(len(exam_flag))
            if len(exam_flag) == 0:
                # 使用issue num来检测是否加载成功，若没加载成功，则重新加载
                pdf_Link = driver.find_element(By.TAG_NAME, 'button').get_attribute("onclick")
                # print(pdf_Link)
                break
            else:
                pdf_Link = "Not Found"
                print("Not Found:", doi_url)
                break
        except TimeoutException:
            print(f"重试 {retry + 1}/{max_retries}: 超时异常发生，继续尝试...")
            # 可以在这里添加额外的重试逻辑，例如刷新页面或者重新加载资源
            driver.refresh()
            time.sleep(2)
    driver.quit()
    return pdf_Link, doi


def find_all_pdf(file_name, processed_row):
    # normally 'doi_list.csv'
    file_exists = os.path.isfile('output.csv')
    with open(file_name, 'r', newline='', encoding="utf-8") as input_file:
        with open('output.csv', 'a' if file_exists else 'w', newline='', encoding='utf-8') as output_file:
            doi_reader = csv.reader(input_file)
            doi_writer = csv.writer(output_file)
            # 遍历每一行
            row_counter = 1
            for row in doi_reader:
                if row_counter <= processed_row:
                    row_counter += 1
                    print("relocated at row ", row_counter)
                # 跳行
                else:
                    if len(row) > 0:
                        doi_url = row[1]
                        print(doi_url)
                        pdf_url, doi = find_pdf_Link(doi_url)
                        if pdf_url.find("'//") != -1:
                            pass
                        else:
                            inserted_text = "//sci-hub.se"
                            pdf_url = pdf_url.replace("location.href='", "location.href='" + inserted_text )
                        print("pdf_url:", pdf_url)
                        if pdf_url == "Not Found":
                            row.append(pdf_url)
                            doi_writer.writerow(row)
                            # print("row:", row)
                            # print("processed")
                        else:
                            status = download_pdf(pdf_url, doi)
                            if status == 1:
                                row.append("Downloaded")
                                doi_writer.writerow(row)
                            elif status == 0:
                                row.append("Found url but 404")
                                doi_writer.writerow(row)
                    print("wait 15s")
                    time.sleep(15)


if __name__ == "__main__":
    # pdf_url_1, doi_1 = find_pdf_Link("http://dx.doi.org/10.1149/1.2124051")
    # print("over")
    # pdf_url_1 = "location.href='//zero.sci-hub.se/4371/2aa19134c17c5c3fe37bd124cd2b7eec/jorne1982.pdf?download=true'"
    # doi_1 = "12345/123"
    # download_pdf(pdf_url_1, doi_1)
    done_row = find_row()
    find_all_pdf("doi_list_rev.csv", done_row)
