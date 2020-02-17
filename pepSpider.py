import os
import traceback

import requests
from lxml import etree

URL_ROOT = "http://bp.pep.com.cn/jc/"


def get_html_doc(url):
    response = requests.get(url, headers=headers)
    response.encoding = "UTF-8"
    return etree.HTML(response.text)


def get_books_download_link(basic_url):
    """
    from html_doc get book info with xpath then return {book: download_url}
    :param basic_url: original url
    :return: books' info with a dict
    """
    html_doc = get_html_doc(basic_url)
    book_dict = {}
    book_li_elements = html_doc.xpath('//*[@id="container"]/div/ul/li')
    for book in book_li_elements:
        name = book.xpath('./a[1]/@title')[0]
        path = book.xpath('./div/a[2]/@href')[0]
        download_url = F"{basic_url}/{path}"
        book_dict.update({name: download_url})
        print(F"{name}: {download_url}")
    return book_dict


def download_book(name, url, output_dir):
    """
    :param name: book's name for preserving
    :param url: book's url for downloading
    :param output_dir: result than output directory
    :return: None
    """
    output_path = F"{output_dir}/{name}.pdf"
    if os.path.exists(output_path):
        print(F"{output_path} 已经存在，跳过")
    else:
        print(F"{output_path} 不存在，现在开始下载")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as fp:
                fp.write(response.content)
            print(F"done: {name}.pdf")


def make_dir(dir_path):
    """
    make a dir to specific path recursively
    :param dir_path: make directory in this path
    :return: None
    """
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        print(F"成功创建文件夹: {dir_path}")
    else:
        if os.path.isdir(dir_path):
            pass
        else:
            os.rename(dir_path, "tmp_dir_name")
            make_dir(dir_path)


def get_grades_dict(html_doc):
    grade_dicts = {}
    container_elements = html_doc.xpath('/html/body/div[2]/div[@class="list_sjzl_jcdzs2020"]')
    for container in container_elements:
        grade = container.xpath('./div[1]/h5/text()')[0]
        url = URL_ROOT + container.xpath('./ul[1]/li[1]/a/@href')[0].split('/')[1]
        grade_dicts.update({grade: url})
        print(F"{grade}: {url}")
    return grade_dicts


def main():
    # get different grades' books info
    html_doc = get_html_doc(URL_ROOT)
    grades_dict = get_grades_dict(html_doc)
    # init an output directory in current path
    root_path = os.getcwd()
    output_path = F"{root_path}/output/"
    make_dir(output_path)
    for grade, url in grades_dict.items():
        try:
            # make working directory
            grade_dir = F"{output_path}/{grade}/"
            make_dir(grade_dir)
            print(F"开始获取书籍链接: {grade}")
            books_dict = get_books_download_link(url)
            # download book
            for name, download_url in books_dict.items():
                download_book(name, download_url, grade_dir)
        except Exception:
            print(F"有一点错误：{traceback.format_exc()}")


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'}
    main()
