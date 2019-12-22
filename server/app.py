from flask import Flask,render_template,session
from SpiderHelper import Spider
from os import path

app = Flask(__name__,static_url_path='/static')
app.secret_key = "sdsfdsgdfgdfgfh"


@app.route('/',methods=['GET'])
def hello_world():
    return render_template('login.html')

@app.route('/get_qr_image_path')
def get_login_qr_image_path():
	session.spider = Spider()
	base_path = path.abspath(path.dirname(__file__))
	file_name = "test.png"
	img_path = path.join(base_path,'static\\')+file_name
	print(img_path)
	session.spider.get_login_image(img_path)
	return "/static/test.png"


if __name__ == '__main__':
    app.run()
