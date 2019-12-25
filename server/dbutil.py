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
        return self.db.moods.find({
            'qq': qq
        })






