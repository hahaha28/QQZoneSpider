# coding=utf-8

from selenium import webdriver
import requests
import re
from urllib import parse
import xlwt
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

    def get_mood(self,qq,file_path):
        url = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
        params = {
            'inCharset': 'utf-8',
            'outCharset': 'utf-8',
            'sort': 0,
            'num': 20,
            'repllyunm': 100,
            'cgi_host': 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6',
            'callback': '_preloadCallback',
            'code_version': 1,
            'format': 'jsonp',
            'need_private_comment': 1,
            'g_tk': self.g_tk
        }
        url = url + parse.urlencode(params)
        t1, pos = True, 0
        url_ = url + '&uin=' + str(qq)

        #建立excel
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('mood')
        worksheet.write(0, 0, "发布时间")
        worksheet.write(0, 1, "发布设备")
        worksheet.write(0, 2, "说说内容")
        worksheet.write(0, 3, "转发数")
        worksheet.write(0, 4, "回复内容")
        worksheet.write(0, 5, "回复数")
        worksheet.write(0, 6, "说说配图")
        row = 1

        while (t1):
            url__ = url_ + '&pos=' + str(pos)
            mood = self.req.get(url=url__, headers=self.headers)
            if '\"msglist\":null' in mood.text:
                t1 = False
            elif "\"message\":\"对不起,主人设置了保密,您没有权限查看\"" in mood.text:
                print("无权访问"+qq)
                return False
            else:
                print("爬取"+qq+"说说")
                # 创建时间
                created_time = re.findall('created_time":\d+', mood.text)
                # 发说说的设备
                source = re.findall('source_appid":".*?"source_name":".*?"', mood.text)
                # 说说内容
                contents = re.findall('],"content":".*?"', mood.text)
                # 转发数
                forword = re.findall('fwdnum":\d+', mood.text)
                # 回复内容
                comment_content = re.findall('commentlist":(null|.*?],)', mood.text)
                # 评论数
                comments = re.findall('cmtnum":\d+', mood.text)
                # 说说配图
                pics = re.findall('","pic(_template|".*?])', mood.text)
                # 点赞的链接
                like_url = 'https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?'
                # 说说的唯一标志
                tids = re.findall('tid":".*?"', mood.text)

                for _time, _source, _content, _forword, _comment_content, _comment, _pic, _tid in \
                        zip(created_time, source, contents, forword, comment_content, comments, pics, tids):
                    # 我要的说说内容
                    mood = {
                        'CreateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(re.sub('created_time":', '', _time)))),
                        'source': re.sub('source_appid":".*?"source_name":"|"', '', _source),
                        'content': re.sub('],"content":"|"', '', _content),
                        'forward': re.sub('fwdnum":', '', _forword),
                        'comment_content': re.sub('null|commentlist":', '', _comment_content) if 'null' in _comment_content else str([(re.sub('content":"|"', '', x), re.sub('createTime2":"|"', '', y), re.sub('name":"|"', '', z), re.sub('uin":', '', zz)) for x, y, z, zz in zip(re.findall('content":".*?"', _comment_content), re.findall('createTime2":".*?"', _comment_content), re.findall('name":".*?"', _comment_content), re.findall('uin":\d+', _comment_content))]),
                        'comment': re.sub('cmtnum":', '', _comment),
                        'pic': [] if 'template' in _pic else [re.sub('url2":|"', '', i) for i in re.findall('url2":".*?"', _pic)]
                    }
                    # print(mood)
                    # 将说说保存在xls中
                    worksheet.write(row,0,mood['CreateTime'])
                    worksheet.write(row,1,mood['source'])
                    worksheet.write(row,2,mood['content'])
                    worksheet.write(row,3,mood['forward'])
                    worksheet.write(row,4,mood['comment_content'])
                    worksheet.write(row,5,mood['comment'])
                    worksheet.write(row,6,mood['pic'])
                    row = row+1
                pos += 20
        workbook.save(file_path)
        return True

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








