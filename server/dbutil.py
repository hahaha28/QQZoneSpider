import pymongo


class DButil:
    def __init__(self):
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client.hhh

    def insert_mood(self,mood,qq):
        mood['qq'] = qq
        self.db.moods.insert_one(mood)

    def insert_info(self,info):
        self.db.infos.insert_one(info)

    def find_info(self,qq):
        result = self.db.infos.find_one({
            'qq': qq
        })
        if result is not None:
            del result['_id']
        return result

    def find_mood(self,qq):
        '''
        :param qq:
        :return:返回列表[{},{}] 或 None
        '''
        result = self.db.moods.find({
            'qq': qq
        })
        list = []
        for r in result:
            del r['_id']
            list.append(r)
        if len(list) == 0:
            return None
        return list

    def find_simple_mood(self,qq):
        result = self.find_mood(qq)
        if result is None:
            return None
        for r in result:
            del r['source']
            del r['forward']
            del r['comment_content']
            del r['comment']
            del r['pic']
        return result











