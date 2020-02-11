import os
import traceback

import requests
from fpdf import FPDF
from lxml import etree


def get_html_doc(url):
    response = requests.get(url, headers=headers)
    response.encoding = "UTF-8"
    return etree.HTML(response.text)


def spider_book_info(html_doc):
    book_info_dicts = {}
    url_li_elements = html_doc.xpath('//*[@id="container"]/div/ul/li[@class="fl"]')
    for li in url_li_elements:
        name = li.xpath('./a/@title')[0]
        url = li.xpath('./a/@href')[0]
        book_info_dicts.update({name: url})
    return book_info_dicts


def download_book_images_to(output_dir, book_name: str, book_url: str):
    book_id = book_url.rsplit('/', maxsplit=2)[1]
    print(F"downloading {book_name} (操作期间请不要动tmp目录) : {output_dir}")
    for image_number in range(1, 1000):  # 1000 页肯定够了
        image_urls = F"http://bp.pep.com.cn/ebooks/{book_id}/files/mobile/{image_number}.jpg"
        response = requests.get(image_urls, headers=headers)
        if response.status_code == 200:
            image_path = F"{output_dir}{image_number}.jpg"
            with open(image_path, 'wb') as fp:
                fp.write(response.content)
            print(F"{image_number}.jpg", end=' ')
        else:
            print(F"{book_name}: {image_number - 1} images")
            break


def images2pdf(from_dir, to_dir, book_name):
    """convert *.jpg files into a pdf in specify directory(from_dir) to destination directory(to_dir)"""
    os.chdir(from_dir)
    images = [image for image in os.listdir(from_dir) if image.endswith('jpg')]
    images.sort(key=lambda x: int(x.split('.')[0]))
    pdf = FPDF()
    for each_image in images:
        if each_image.endswith('.jpg'):
            pdf.add_page()
            pdf.image(each_image, x=5, y=5, w=200, h=290, type='jpg')
    else:
        os.chdir(to_dir)
        output_book_name = F"{book_name}.pdf"
        pdf.output(output_book_name)


def make_or_rename_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        make_or_rename_dir(dir_path)
    else:
        if os.path.isdir(dir_path):
            pass
        else:
            os.rename(dir_path, "tmp_dir_name")
            os.mkdir(dir_path)
            make_or_rename_dir(dir_path)


def main():
    url_dicts = {
        '义务教育教科书': 'http://bp.pep.com.cn/jc/ywjyjks/ywjygjkcjc/index.html',
        '义务教育教科书（五·四学制）': 'http://bp.pep.com.cn/jc/ywjyjks/ywjygjkcjc54z/index.html',
        '普通高中教科书': 'http://bp.pep.com.cn/jc/gzjks/ptgzjks/index.html',
        '普通高中课程标准实验教科书': 'http://bp.pep.com.cn/jc/gzjks/ptgzkcbzsyjks/index.html',
    }

    # make directory_root
    original_path = os.getcwd()
    make_or_rename_dir(F"{original_path}/output/")
    for k, url in url_dicts.items():
        try:
            # make directory_leaf
            output_dir = F"{original_path}/output/{k}/"
            tmp_output_dir = F"{original_path}/output/{k}/tmp/"
            make_or_rename_dir(output_dir)
            make_or_rename_dir(tmp_output_dir)
            print(F"Output directory: {output_dir}\nTmp directory: {tmp_output_dir}")

            # crawling
            html_doc = get_html_doc(url)
            book_info_dicts = spider_book_info(html_doc)
            print(book_info_dicts)
            for book_name, book_url in book_info_dicts.items():
                # check exists
                os.chdir(output_dir)
                if os.path.exists(F"{book_name}.pdf"):
                    print(F"{book_name}.pdf 已存在，开始下一个")
                    continue
                print(F"{book_name}.pdf 不存在，开始下载")

                # truncate tmp directory
                os.chdir(tmp_output_dir)
                [os.remove(file) for file in os.listdir('.')]
                print("tmp 目录清空成功!")

                # download images to tmp directory
                download_book_images_to(tmp_output_dir, book_name=book_name, book_url=book_url)

                # convert images(JPG) into a PDF file
                print("开始合并为 PDF...")
                images2pdf(from_dir=tmp_output_dir, to_dir=output_dir, book_name=book_name)
                print(F"{book_name} done!")
            else:
                os.chdir(tmp_output_dir)
                [os.remove(file) for file in os.listdir('.')]
                print("tmp 目录清空成功!")
                print("done!")
                print("-----------" * 10)
        except Exception:
            print(F"有一点错误：{traceback.format_exc()}")


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'}
    main()
