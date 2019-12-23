# coding=utf-8

from selenium import webdriver
import requests
import re
from urllib import parse
import xlwt


class Spider:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get('https://i.qq.com/')
        self.headers = {
            'host': 'h5.qzone.qq.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'connection': 'keep-alive'
        }
        self.req = requests.Session()
        self.cookies = {}

    def get_qr_image_path(self):
        '''
        获得登录二维码的连接
        :return: 登录二维码连接
        '''
        self.driver.switch_to.frame('login_frame')
        qr_image_path = self.driver.find_element_by_id('qrlogin_img').get_property('src')
        return qr_image_path

    def get_login_image(self, file_path):
        '''
        获取登录二维码的截图
        :param file_path: 截图保存路径
        :return:
        '''
        self.driver.switch_to.frame('login_frame')
        png = self.driver.find_element_by_id('qrlogin_img').screenshot_as_png
        with open(file_path, 'wb') as img:
            img.write(png)

    def login(self):
        '''
        登录QQ空间
        :return: 成功则返回true
        '''
        cur_url = self.driver.current_url
        if re.match('https://user.qzone.qq.com/(\d+)$', cur_url) != None:
            self.my_qq_num = re.sub(r'\D', "", cur_url)  # qq号
            # self.driver.get('http://user.qzone.qq.com/{}'.format(self.my_qq_num))
            cookie = ''
            for item in self.driver.get_cookies():
                cookie += item["name"] + '=' + item['value'] + ';'
            self.cookies = cookie
            self.get_g_tk()
            self.headers['Cookie'] = self.cookies
            self.driver.quit()
            return True
        else:
            return False

    def get_friends_url(self):
        '''
        构造好友请求链接
        :return: 链接
        '''
        url = 'https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?'
        params = {
            'uin': self.my_qq_num,
            'ver': 1,
            'fupdate': 1,
            'action': 1,
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        return url

    def get_friends(self,file_path):
        '''
        获取全部好友
        :return: 好友以及对应QQ列表
        '''
        offset, t = 0, True
        url = self.get_friends_url()
        name, qq_num = [], []

        while (t):
            url_ = url + '&offset=' + str(offset)
            page = self.req.get(url=url_, headers=self.headers)
            if ('\"end\":1' and '\"uinlist\":[]') in page.text:
                t = False
            else:
                names, qqs = re.findall('label":.*"', page.text), re.findall('"\d+"', page.text)
                for _, __ in zip(names, qqs):
                    name.append(re.sub('label":|"', '', _))
                    qq_num.append(re.sub('"', '', __))
            offset += 50
        self.name, self.qq_num = name, qq_num
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('friend_list')
        worksheet.write(0,0,"姓名")
        worksheet.write(0,1,"QQ号")
        i = 1
        for na in name:
            worksheet.write(i, 0, na)
            worksheet.write(i, 1, qq_num[i-1])
            i=i+1
        workbook.save(file_path)

    def get_g_tk(self):
        '''
        获取g_tk()
        :return: 生成的g_tk
        '''
        p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        print('g_tk', h & 2147483647)
        self.g_tk = h & 2147483647








