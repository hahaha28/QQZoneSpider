from flask import Flask, render_template, session, request
from SpiderHelper import Spider
from os import path
import random

app = Flask(__name__, static_url_path='/static')

app.secret_key = "sdsfdsgdfgdfgfh"
spider_temp = {}


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('login.html')

@app.route('/test')
def test():
    return "ok"

@app.route('/test2')
def test2():
    return render_template('test.html')

@app.route('/function')
def function():
    return render_template('function.html')


@app.route('/get_qr_image_path')
def get_login_qr_image_path():
    spider = Spider()
    key = get_random_key()
    spider_temp[key] = spider
    session['key'] = key
    base_path = path.abspath(path.dirname(__file__))
    file_name = get_random_file_name()
    img_path = path.join(base_path, 'static\\') + file_name
    print(img_path)
    spider.get_login_image(img_path)
    return "/static/" + file_name


@app.route('/flush_qr_image')
def flush_qr_image():
    key = session.get('key')
    spider = spider_temp[key]
    base_path = path.abspath(path.dirname(__file__))
    file_name = get_random_file_name()
    img_path = path.join(base_path, 'static\\') + file_name
    spider.flush_login_image(img_path)
    return "/static/" + file_name


@app.route('/confirm_login')
def confirm_login():
    key = session.get('key')
    spider = spider_temp[key]
    if spider.login():
        return "success"
    else:
        return "error"


@app.route('/get_friends_qq_and_name')
def get_friends_qq_name():
    key = session.get('key')
    spider = spider_temp[key]
    base_path = path.abspath(path.dirname(__file__))
    file_name = spider.my_qq_num + "friendList.xls"
    file_path = path.join(base_path, 'static\\') + file_name
    spider.get_friends(file_path)
    return file_name


@app.route('/get_mood')
def get_one_mood():
    qq = request.args.to_dict()['qq']
    key = session.get('key')
    spider = spider_temp[key]
    json_data = spider.get_mood(qq)
    print("json_data=")
    print(json_data)
    if json_data is not None:
        # return render_template('show_mood.html',data=json_data,qq=qq)
        return json_data
    else:
        return "error"


@app.route('/show_mood')
def show_mood():
    return render_template('show_mood.html')


@app.route('/download_mood')
def download_mood():
    qq = request.args.to_dict()['qq']
    key = session.get('key')
    spider = spider_temp[key]
    base_path = path.abspath(path.dirname(__file__))
    file_name = qq + "_mood.xls"
    file_path = path.join(base_path, 'static\\') + file_name
    spider.write_mood_to_xls(qq,file_path)
    return file_name

@app.route('/get_info')
def get_one_info():
    qq = request.args.to_dict()['qq']
    key = session.get('key')
    spider = spider_temp[key]
    # base_path = path.abspath(path.dirname(__file__))
    # file_name = qq + "_info.xls"
    # file_path = path.join(base_path, 'static\\') + file_name
    info = spider.get_info(qq)
    print(info)
    if info is not None:
        return render_template('show_info.html',data=info)
    else:
        return "error"


def get_random_file_name():
    while True:
        num = random.randrange(10000000)
        base_path = path.abspath(path.dirname(__file__))
        file_name = str(num) + ".png"
        img_path = path.join(base_path, 'static\\') + file_name
        if not path.exists(img_path):
            return file_name


def get_random_key():
    while True:
        num = random.randrange(10000000)
        if not num in spider_temp:
            return str(num)


if __name__ == '__main__':
    app.config["JSON_AS_ASCII"] = False
    app.run()
