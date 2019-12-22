# coding=utf-8

from selenium import webdriver
import requests
import re
import time


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

    def get_login_image(self,file_path):
        '''
        获取登录二维码的截图
        :param file_path: 截图保存路径
        :return:
        '''
        self.driver.switch_to.frame('login_frame')
        png = self.driver.find_element_by_id('qrlogin_img').screenshot_as_png
        with open(file_path,'wb') as img:
            img.write(png)

    def login(self):
        '''
        登录QQ空间
        :return: 成功则返回true
        '''
        time.sleep(5)   #暂停5秒等待网页加载
        cur_url = self.driver.current_url
        if re.match('https://user.qzone.qq.com/(\d+)$',cur_url) != None:
            self.qqNum = re.sub(r'\D',"",cur_url)   #qq号
            self.driver.get('http://user.qzone.qq.com/{}'.format(self.qqNum))
            cookie = ''
            for item in self.driver.get_cookies():
                cookie += item["name"] + '=' + item['value'] + ';'
            self.cookies = cookie
            self.get_g_tk()
            self.headers['Cookie'] = self.cookies
            self.driver.quit()
            return True
        else:
            self.driver.quit()
            return False

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









