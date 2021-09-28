import csv
import json
import math

from icecream import ic

from bs4 import BeautifulSoup

from dao.MySqlConn import MyPymysqlPool
from spiders.page_getter import PageGetter


class Spider:
    """
    具体的爬虫对象
    """

    # 爬所有的分类
    def get_classify(self, url):
        """
        爬取所有的分类
        :param url:
        :return:
        """
        page = PageGetter().get_page(url=url)
        soup = BeautifulSoup(page, 'html.parser')
        classes_div = soup.select(".listL div")
        res = []
        for type in classes_div:
            type_soup = BeautifulSoup(str(type), 'html.parser')
            type_url = type_soup.select_one("a")['href']
            type_name = type_soup.select_one("nobr").text

            res.append({
                "type_url": f"http://12345.chengdu.gov.cn/{type_url}&page=",
                "type_name": type_name
            })
        return res

    # 获取一个类型的分类下一共有多少页
    def get_type_total_pages(self, url):
        """
        获取一个类型的分类下一共有多少页
        :param url:
        :return:
        """
        ic(url)
        page = PageGetter().get_page(url=url)
        import re
        iRecCount = re.findall('var iRecCount = [0-9]*', page)
        news_count = int(str(iRecCount[0]).split("=")[1].strip())
        page_count = math.ceil(news_count / 15)
        return page_count

    # 获取基础信息
    def get_call_base_info(self, url, type_name):
        page_getter = PageGetter()
        page = page_getter.get_page(url=url)
        soup = BeautifulSoup(page, 'html.parser')
        lis = soup.select("li.f12px")
        # 获取每一条电话信息
        for li in lis:
            a_soup = BeautifulSoup(str(li), 'html.parser')
            a = a_soup.select_one("a")
            cell = a_soup.select("div")
            item = {
                "url": f"http://12345.chengdu.gov.cn/{a['href']}",
                "call_title": cell[0].text,  # 来电标题
                "handling_unit": cell[1].text,  # 办理单位
                "status": cell[2].text,  # 状态
                "category": cell[3].text,  # 类别
                "visit_volume": cell[4].text,  # 访问量
                "tile": cell[5].text,  # 时间
                "type_name": type_name  # 分类名
            }
            # 获取电话信息详情，也就是点进去的地方
            res_item = self.get_call_detail_info(item, page_getter)
            # 把结果保存到mysql
            self.save_in_mysql(item)
            # res.append(res_item)
            ic(res_item['call_title'])

    # 根据标题爬取一个来电的详细信息
    def get_call_detail_info(self, item, page_getter):
        """
        根据标题爬取一个来电的详细信息
        :param item:
        :param page_getter:
        :return:
        """
        detail_page = page_getter.get_page(item['url'])
        detail_soup = BeautifulSoup(str(detail_page), 'html.parser')
        detail_cells = detail_soup.select(".tb .td2")
        # 电话内容
        item['call_content'] = detail_cells[2].text
        # 处理结果
        item['handle_result'] = detail_soup.select(".tb td")[-1].text
        return item

    # 保存结果到mysql
    # 保存结果到json
    def save_in_mysql(self, item):
        f = open("政府来电结果.json", 'a+', encoding='utf-8')
        json.dump(item, f, ensure_ascii=False)
        f.write(",\n")
        f.close()
    # mysql = MyPymysqlPool()
    # sql = "insert into call_info(url,call_title,handling_unit,status,category,visit_volume,tile,type_name,call_content,handle_result) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    # param = (item['url'], item['call_title'], item['handling_unit'], item['status'],
    #          item['category'], item['visit_volume'], item['tile'],
    #          item['type_name'], item['call_content'], item['handle_result'])
    # mysql.insert(sql=sql, param=param)
