import json
from flask import Flask, request, session, jsonify
from . import bappy_db
from datetime import datetime

host = '18.118.131.221'
db_id = 'benny'
pw = 'benny'
db_name = 'bappy_web'

def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

class Hangout_Data():
    def __init__(self):
        self.index = 0
        self.title = ""
        self.meet_time = ""
        self.location = ""
        self.profile_image = []
        self.nation_image = []
        self.age = []
        self.gender = []
        self.join = "join"
        self.join_url = "" # cancel join redirct
        self.location_url = "naver.com"
        self.openchat = ""

    def make_hangout_data(self,Hangout):
        self.index = Hangout.idx
        self.title = Hangout.title
        self.meet_time = Hangout.meet_time
        self.location = Hangout.location
        self.location_url = Hangout.location_url

        images = str_to_li(Hangout.participants_image)
        nations = str_to_li(Hangout.participants_nation)
        ages = str_to_li(Hangout.participants_age)
        gender = str_to_li(Hangout.participants_gender)

        for i in range(Hangout.participants_num):
            self.profile_image.append(images[i])
            #self.nation_image.append(nations[i])
            self.nation_image.append("usa")
            self.age.append(ages[i])
            self.gender.append(gender[i])

        for i in range(4-Hangout.participants_num):
            self.profile_image.append("person")
            self.nation_image.append("nation")
            self.age.append("?")
            self.gender.append("?")

        # it is my hangout
        #print(str_to_li(Hangout.participants_id))
        if 'user_id' in session and session['user_id'] in str_to_li(Hangout.participants_id):
            self.join="cancel"
            self.join_url = "/hangout/cancel"
            self.openchat = Hangout.openchat

        else:
            self.join = "join"
            self.join_url = "/hangout/join"
            self.openchat = "none"







        #--- 이미지
        #if Hangout.image == ""
        #self.image = ""

class Hangout():
    def __init__(self,idx):
        self.idx = idx
        self.participants_id = ""
        self.participants_nation = ""
        self.participants_image = ""
        self.participants_num = 0
        self.participants_gender = ""
        self.participants_age = ""
        self.click_num = 0
        self.openchat = ""
        self.location = ""
        self.title = ""
        self.meet_time = ""
        self.register_time = ""
        self.city=""
        self.woman=0
        self.man=0
        self.location_url=""
#print(datetime.now())
    def create_hangout(self, request):
        self.openchat = request.form.get('openchat')
        self.location = request.form.get('location')
        self.title = request.form.get('title')
        self.meet_time = request.form.get('meet_time')
        self.register_time = datetime.now().strftime('%m-%d %H:%M')
        self.city= request.form.get('city')
        self.location_url = request.form.get('location_url')

class HangoutDao():
    def __init__(self):
        self.database = bappy_db.Database()

    def find_user_li(self,users_id,user_id):
        for i in range(len(users_id)):
            if users_id[i] ==  user_id:
                return i
        return "there are no user id"

    def get_hangout_byidx(self,idx):
        sql = """select * from bp_hangout where  idx = %s"""%(idx)
        return self.database.executeOne(sql)

    def cancel_hangout_byidx(self,idx,user_id, user_nation, user_gender, user_age):
        hangout = self.get_hangout_byidx(idx)
        users_id = str_to_li(hangout['hg_participants_id'])
        users_nation = str_to_li(hangout['hg_participants_nation'])
        users_image = str_to_li(hangout['hg_participants_image'])
        users_age = str_to_li(hangout['hg_participants_age'])
        users_gender = str_to_li(hangout['hg_participants_gender'])
        users_num = hangout['hg_participants_num']
        users_man = hangout['hg_man']
        users_woman = hangout['hg_woman']
        index = self.find_user_li(users_id, user_id)
        print("삭제해야할 인덱스는 ",index)
        users_id.pop(index)
        users_nation.pop(index)
        users_image.pop(index)
        users_age.pop(index)
        users_gender.pop(index)
        users_num -= 1
        if user_gender == 'man':
            users_man -= 1
        else:
            users_woman -= 1

        users_id = list_to_str(users_id)
        users_nation = list_to_str(users_nation)
        users_image = list_to_str(users_image)
        users_gender = list_to_str(users_gender)
        users_age = list_to_str(users_age)
        users_num = str(users_num)


        return self.update_hangout(idx, users_image,users_id, users_nation, users_gender, users_age,users_num, users_man, users_woman)


    def update_hangout(self,idx,users_image, users_id, users_nation, users_gender, users_age, users_num, users_man, users_woman):
        sql = """ update bp_hangout set hg_man = '%s', hg_woman = '%s', hg_participants_id = '%s', hg_participants_nation = '%s', hg_participants_image = '%s', hg_participants_age = '%s', hg_participants_gender = '%s', hg_participants_num = '%s' where idx = '%s'"""% (users_man,users_woman,users_id,users_nation,users_image,users_age,users_gender, users_num, idx)
        self.database.execute(sql)
        return "true"


    def join_hangout_byidx(self,idx,user_id, user_nation, user_gender, user_age):
        hangout = self.get_hangout_byidx(idx)

        if hangout["hg_"+user_gender] >=2: #check
            return "false"

        users_id = str_to_li(hangout['hg_participants_id'])
        users_nation = str_to_li(hangout['hg_participants_nation'])
        users_image = str_to_li(hangout['hg_participants_image'])
        users_age = str_to_li(hangout['hg_participants_age'])
        users_gender = str_to_li(hangout['hg_participants_gender'])
        users_num = hangout['hg_participants_num']
        users_man = hangout['hg_man']
        users_woman = hangout['hg_woman']

        if user_gender == "man":
            users_man += 1
        else:
            users_woman += 1



        users_id.append(user_id)
        users_nation.append(user_nation)
        users_image.append("bird")
        users_gender.append(user_gender)
        users_age.append(user_age)
        users_num +=1

        users_id = list_to_str(users_id)
        users_nation = list_to_str(users_nation)
        users_image = list_to_str(users_image)
        users_gender = list_to_str(users_gender)
        users_age = list_to_str(users_age)
        users_num = str(users_num)

        sql = """ update bp_hangout set hg_man = '%s', hg_woman = '%s', hg_participants_id = '%s', hg_participants_nation = '%s', hg_participants_image = '%s', hg_participants_age = '%s', hg_participants_gender = '%s', hg_participants_num = '%s' where idx = '%s'"""% (users_man,users_woman,users_id,users_nation,users_image,users_age,users_gender, users_num, idx)
        print(sql)

        self.database.execute(sql)

        return "true"




    def count_hangout(self):
        sql = """select count(0) as cnt from bp_hangout"""
        return self.database.executeAll(sql)[0]['cnt']

    def insert_hangout(self, hangout):
        sql = """
        INSERT INTO bp_hangout (hg_location_url,hg_man,hg_woman,hg_city,idx, hg_participants_num, hg_click_num, hg_openchat, hg_location, hg_title, hg_meet_time, hg_register_time)
        VALUES ('%s','%d','%d','%s','%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s')
        """%(hangout.location_url,0,0,hangout.city,hangout.idx, hangout.participants_num, hangout.click_num,hangout.openchat,hangout.location,hangout.title,hangout.meet_time,hangout.register_time)
        self.database.execute(sql)

    def get_hangout_list(self):
        sql = """
        select * from bp_hangout
        """
        res = self.database.executeAll(sql)
        hangout_list = []
        for h in res:
            hangout = Hangout(h['idx'])
            hangout.idx = h['idx']
            hangout.participants_id = h['hg_participants_id']
            hangout.participants_nation = h['hg_participants_nation']
            hangout.participants_image = h['hg_participants_image']
            hangout.participants_num = h['hg_participants_num']
            hangout.click_num = h['hg_click_num']
            hangout.hg_openchat = h['hg_openchat']
            hangout.location = h['hg_location']
            hangout.title = h['hg_title']
            hangout.participants_gender = h['hg_participants_gender']
            hangout.participants_age = h['hg_participants_age']
            hangout.meet_time = h['hg_meet_time']
            hangout.register_time = h['hg_register_time']
            hangout.city = h['hg_city']
            hangout.man = h['hg_man']
            hangout.woman = h['hg_woman']
            hangout.location_url = h['hg_location_url']
            hangout_list.append(hangout)
        return hangout_list

    def get_hangout_data_list(self):
        hl = self.get_hangout_list()
        hangout_data_list = []
        for h in hl:
            hangout_data = Hangout_Data()
            hangout_data.make_hangout_data(h)
            hangout_data_list.append(hangout_data)
        return hangout_data_list

def list_to_str(li):
    if len(li)==1:
        return str(li[0])
    for i in range(len(li)):
        li[i]=str(li[i])
    return ','.join(li)
# "1,2,3,4"->[1,2,3,4]
def str_to_li( db_str):
    db_str = str(db_str)
    if db_str == "None":
        return []
    if db_str ==  "":
        return []
    return db_str.split(',')
