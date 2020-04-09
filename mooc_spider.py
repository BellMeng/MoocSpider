from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium import common
from lxml import etree
import pymysql
import random
import time


class Mooc:
    url_list = []

    def __init__(self, options=None, url_list=None):
        self.err_count = 0
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(10)
        if url_list:
            self.url_list = url_list

    def _parse_course_list(self, course_list):
        for i, course in enumerate(course_list):
            print("===============第%d个============" % (i + 1,))
            div_str = etree.tostring(course, encoding="utf-8")
            course_html = etree.HTML(div_str.decode())
            course_url = "https://www.icourse163.org" + course_html.xpath("//div[@class='u-clist f-bgw f-cb f-pr j-href ga-click']/@data-href")[0]
            course_name = course_html.xpath("//span[@class=' u-course-name f-thide']/text()")[0]
            print(course_name)
            university_name = course_html.xpath("//a[@class='t21 f-fc9']/text()")[0]
            print(university_name)
            teachers = course_html.xpath("//a[@class='f-fc9']/text()")
            if len(teachers) > 5:
                teachers = teachers[0:5]
                teachers[4] += "等"
            all_teachers = "、".join(teachers)
            print(all_teachers)
            self._insert_data(course_name.strip(), "中国大学MOOC", university_name.strip(), course_url.strip(), all_teachers.strip())

    def _get_all_pages(self, page_source):
        page_html = etree.HTML(page_source)
        page_number = int(
            page_html.xpath("//div[@class='course-card-list-pager ga-click f-f0']//li[last()-1]/a")[0].text)
        # page_number = 2
        page_count = 1
        while True:
            print("################第%d页###############" % (page_count,))
            course_list = page_html.xpath(
                "//div[@class='m-course-list']/div/div[@class='u-clist f-bgw f-cb f-pr j-href ga-click']")
            self._parse_course_list(course_list)
            if page_number == 1:
                break
            try:
                time.sleep(random.random() * 4)
                self.browser.find_element_by_xpath(
                    "//div[@class='course-card-list-pager ga-click f-f0']//li[last()]/a").click()
                time.sleep(1)
                page_html = etree.HTML(self.browser.page_source)
            except common.exceptions.ElementNotInteractableException:
                print("找不到了")
                print(self.browser.current_url)
                break
            page_number -= 1
            page_count += 1

    def _connect_mysql(self):
        self.conn = pymysql.connect(host="127.0.0.1", user="root", password="password", database="mooc_info")

    def _insert_data(self, course_name, course_source, university, url, teachers):
        cursor = self.conn.cursor()
        sql = "insert into course_list (course_name, course_source, affiliated_university, url, teachers) values (%s, %s, %s, %s, %s);"
        try:
            cursor.execute(sql, [course_name, course_source, university, url, teachers])
            self.conn.commit()
        except pymysql.Error as e:
            self.err_count += 1
            print("插入数据失败！")
            print(e.args[0], e.args[1])
            self.conn.rollback()

    def start(self):
        print("开始了")
        self._connect_mysql()
        for url in self.url_list:
            self.browser.get(url)
            time.sleep(random.randint(1, 3) * 2)
            page_source = self.browser.page_source
            self._get_all_pages(page_source)
        print("共", self.err_count, "条未插入")
    # def __del__(self):
    #     self.browser.close()


if __name__ == "__main__":
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    url_list = [
        'https://www.icourse163.org/category/computer',
        'https://www.icourse163.org/category/science',
        'https://www.icourse163.org/category/foreign-language',
        'https://www.icourse163.org/category/ECO',
        'https://www.icourse163.org/category/management%20theory',
        'https://www.icourse163.org/category/biomedicine',
        'https://www.icourse163.org/category/literature',
        'https://www.icourse163.org/category/engineering',
        'https://www.icourse163.org/category/art-design',
        'https://www.icourse163.org/category/psychology',
        'https://www.icourse163.org/category/law',
        'https://www.icourse163.org/category/teaching-method',
        'https://www.icourse163.org/category/historiography',
        'https://www.icourse163.org/category/agriculture',
        'https://www.icourse163.org/category/philosophy',
    ]
    spider = Mooc(options=options, url_list=url_list)
    spider.start()
