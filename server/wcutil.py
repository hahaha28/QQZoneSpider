# coding=utf-8 #
import re
import wordcloud
import jieba
from dbutil import DButil

def deal_content(mood):
    moudle = re.compile('@{.*}')
    str = moudle.sub('', mood)
    moudle = re.compile('\[em\].*em\]')
    str = moudle.sub('', str)
    moudle = re.compile(r'\\n')
    str = moudle.sub(r'\r\n',str)
    return str


def write_content(moods, file_path):
    f = open(file_path, 'w',encoding='utf-8')
    for mood in moods:
        content = deal_content(mood['content'])
        f.write(content)
        f.write('\r\n')
    f.close()

def generate_word_cloud(source_file_path,to_file_path):
    with open(source_file_path, 'r', encoding='utf-8') as w:
        t = w.read()
    ls = jieba.lcut(t)
    text = "".join(ls)
    w = wordcloud.WordCloud(font_path="C:/Windows/Fonts/simfang.ttf", width=1000, height=800, background_color='white')
    w.generate(text)
    w.to_file(to_file_path)

if __name__ == '__main__':
    # db = DButil()
    # moods = db.find_mood('915140276')
    # write_content(moods,"E://test.txt")
    generate_word_cloud("E://text.txt","E://test.jpg")
