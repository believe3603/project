import time
import sys
import datetime
import ssl
import socket
import requests
from urllib.request import urlopen, Request, URLError, HTTPError
import os


USERAGENT = 'tis/modistool.py_1.0--' + sys.version.replace('\n', '').replace('\r', '')

class Modistool():
    def __init__(self, token=None, type=None, source=None, destination=None, start_date=None, end_date=None, striptup=None):
        """
            :param token: 用于nasa认证的token，需要申请
            :param type: 卫星数据类型
            :param source: 下载卫星数据的链接地址
            :param destination: 存储卫星数据的目录
            :param start_date: 开始时间
            :param end_date: 结束时间
            :param striptup: 条带号
        """
        self.type = type
        self.token = token
        self.source = source
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.striptup = striptup


    # 根据日期获取该日期在一年中的天数
    def get_days(self, date):
        """
            A date is given, return back which days in a year.
            :param date: 日期字符串，例如：'2019-10-21'
            :return: 该日期在当年的天数，int类型，例如294
        """
        date = time.strptime(date, '%Y-%m-%d')
        return date.tm_yday


    # 根据日期获取年份
    def get_year(self, date):
        """
            根据日期返回年份
            :param date: 字符串格式的日期，例如'2019-10-21'
            :return: 返回年份，int类型
        """
        year = int(date.split('-')[0])
        return year


    # 获取待下载的所有日期列表
    def get_date_list(self):
        """
            根据开始日期，结束日期，返回中间的所有的日期
            :return: date_list 日期列表
        """
        sdate = self.start_date
        edate = self.end_date
        syear = self.get_year(sdate)
        eyear = self.get_year(edate)
        if syear != eyear:
            print('时间相差太大，数据量太多，可能会被nasa站点拒绝，请缩小范围')
            sys.exit(0)
        date_list = []
        s_date = datetime.datetime.strptime(sdate, '%Y-%m-%d')
        e_date = datetime.datetime.strptime(edate, '%Y-%m-%d')
        while s_date <= e_date:
            # datetime.datetime转str
            s_date = s_date.strftime('%Y-%m-%d')
            date_list.append(s_date)
            # str转datetime.datetime
            s_date = datetime.datetime.strptime(s_date, '%Y-%m-%d')
            s_date += datetime.timedelta(days=1)
        return date_list


    # 处理url列表
    def handle_url(self, url):
        """
            根据传入的url，返回一个数据列表
            :param url: 要下载的网页的csv地址,例如：https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6/MOD09A1/2019/281.csv
            :return: 返回一个可下载列表，list类型
        """
        headers = {'user-agent': USERAGENT}
        day_list = []
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            fh = urlopen(Request(url, headers=headers), timeout=30, context=ctx)
            result = fh.readlines()[1:]
            for i in result:
                day = str(i).split(',')[0].split("'")[1]
                day_list.append(day)
            return day_list
        except socket.timeout as e:
            print('请求超时')
            return -1
        except URLError as e:
            print('连接失败，失败原因是：%s'% e.reason, file=sys.stderr)


    # 返回可以下载的日期
    def get_down_date(self):
        """
            根据url获取可以下载的日期列表
            :return: 返回可以下载的列表
        """
        url = "{}/{}/{}/{}".format(self.source, self.type, str(self.get_year(self.start_date)), '.csv')
        count_list = []
        get_date = []
        get_filelist = []
        daylist = self.handle_url(url)
        # 获取要下载的天数列表
        for j in self.get_date_list():
            count = self.get_days(j)
            count_list.append(count)

        # 获取可以下载的天数列表
        for m in count_list:
            if str(m) in daylist:
                get_date.append(m)
        if len(get_date) == 0:
            print('网站还没更新数据，请更新后在下载！')
            sys.exit(0)
        # 获取可以下载天数的csv的url地址
        for file in get_date:
            file_url = "{}{}/{}/{}{}".format(self.source, self.type, str(self.get_year(self.start_date)), file, '.csv')
            get_filelist.append(file_url)
        get_file_all_list = []
        # 获取所有的要下载的文件列表
        for h in get_filelist:
            file_list = self.handle_url(h)
            get_file_all_list.append(file_list)
        return get_file_all_list, get_date


    # 根据条带号获取到对应的下载文件
    # stripTup = ["h27v06", "h28v06", "h27v05"]
    def down_striptup(self):
        """
            获取指定条带号的下载文件列表
            :return: 条带号的下载列表，list类型
        """
        m = 0
        count = 1
        striptup_list = []
        tup = self.striptup
        file_all_list, d = self.get_down_date()
        count_cycle = len(tup)
        # 循环过滤需要下载的条带号文件
        while count_cycle:
            for i in tup:
                for j in file_all_list[m]:
                    if i == j.split('.')[2]:
                        striptup_list.append(j)
                count += 1
                if count > 3:
                    m += 1
                    count = 1
            count_cycle -= 1

        return striptup_list


    # 多线程下载
    def thead_download(self, n, se):
        pass


    # 下载文件
    def download(self):
        """
            下载文件
            :return:
        """
        down_file_list = self.down_striptup()
        k, v = self.get_down_date()
        down_url = []
        for i in v:
            for j in down_file_list:
                if i == int(j.split('.')[1][-3:]):
                    url = "{}{}/{}/{}/{}".format(self.source, self.type, str(self.get_year(self.start_date)), i, j)
                    down_url.append(url)
        for m in down_url:
            print("downloading with " + os.path.basename(m))
            LocalPath = os.path.join(self.destination, os.path.basename(m))
            r = requests.get(m)
            with open(LocalPath, "wb") as code:
                code.write(r.content)
        print('下载完成')


if __name__ == '__main__':
    stripTup = ["h27v06", "h28v06", "h27v05"]
    destination = r'G:\20190926hb'
    download = Modistool(source='https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6/', \
                         type='MOD09A1', start_date='2019-09-15', end_date='2019-10-20', striptup=stripTup, destination=destination)

    download.download()