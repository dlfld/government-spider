import threading

import requests
from icecream import ic

from spiders.call_classify_spider import Spider


def save_exception(e):
    with open("except.txt", "a") as file:
        file.write(str(e))


def run(type):
    # 获取当前电话类别下一共有多少页
    page_number = spider.get_type_total_pages(f"{type['type_url']}1")
    # 遍历每一页进行爬取
    for current_pn in range(1, page_number + 1):
        try:
            # 爬取每一页的每一个电话信息
            spider.get_call_base_info(f"{type['type_url']}{current_pn}", type['type_name'])
        except Exception as e:
            ic(e)
            save_exception(e)


if __name__ == '__main__':
    # 实例化一个spider对象
    spider = Spider()
    # 爬取电话类别信息
    types = spider.get_classify("http://12345.chengdu.gov.cn/moreTelByClass?TelType=1101&page=2")
    ic(len(types))
    for type in types:
        # 每一个类别开启一个线程进行爬取
        threading.Thread(target=run, args=(type,)).start()
