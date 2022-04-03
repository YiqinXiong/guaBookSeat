import os
import requests
import logging
import time, datetime
from json import load as json_load

logging.basicConfig(level=logging.INFO, filename="guaBookSeat.log", encoding='utf-8')

def get_start_time(conf_start_time):
    # 获取今日0点时间戳
    now_hour = datetime.datetime.now().hour
    today = datetime.date.today()
    today_timestamp = int(time.mktime(today.timetuple()))
    # 若今日未到22:00，则预约今日自习室，否则预约明日自习室
    return (today_timestamp + 3600*conf_start_time) if now_hour < 22 else (today_timestamp + 86400 + 3600*conf_start_time)

def get_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class SeatBooker():
    def __init__(self) -> None:
        try:
            with open('config.json', 'r') as fp:
                conf = json_load(fp)
        except FileNotFoundError:
            logging.error("无配置文件，请先使用 \"python3 create_config.py\" 生成配置文件")
            exit(-1)
        # 读取参数配置
        self.username = conf['username']
        self.password = conf['password']
        self.content_id = conf['content_id']
        self.start_time = get_start_time(conf['start_time'])
        self.duration = 3600*conf['duration']
        self.seat_id = conf['seat_id']
        self.category_id = conf['category_id']
        self.target_seat = ""
        self.target_seat_title = ""
        # 建链相关
        self.session = requests.session()
        url_home = 'https://jxnu.huitu.zhishulib.com'
        self.urls = {
            'login' : url_home + '/api/1/login',
            # 'get_uid' : url_home + '/Station/Station/getUnreadMessageCount?LAB_JSON=1', # 其实可以在login的post动作的response中找到
            'search_seat' : url_home + '/Seat/Index/searchSeats?LAB_JSON=1',
            'book_seat' : url_home + '/Seat/Index/bookSeats?LAB_JSON=1',
            'get_my_booking_list' : url_home + '/Seat/Index/myBookingList?LAB_JSON=1'
        }
        self.fake_header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
            'Referer':'https://jxnu.huitu.zhishulib.com/'
        }
    

    def login(self):
        data = {
            "login_name" : self.username,
            "password" : self.password,
            "ui_type" : "com.Raw",
            "code" : "ef4037d86e78f28fee8eca00d1a16e50",
            "str" : "ViCRcuEKGnrVH3eM",
            "org_id" : "142",
            "_ApplicationId" : "lab4",
            "_JavaScriptKey" : "lab4",
            "_ClientVersion" : "js_xxx",
            "_InstallationId" : "f28639d1-5c15-1fa0-89bd-9da5a8e015e0"
        }

        try:
            response = self.session.post(self.urls['login'], json=data, headers=self.fake_header)
        except requests.exceptions.ReadTimeout:
            logging.error(f'[{get_now()}] login页面超时无响应')
            exit(-1)

        if response.status_code == 200:
            response_data = response.json()
            if response_data["gender"] == "2":
                nick_name = f'美女<{response_data["name"]}>' if response_data["name"] != "刘庭华" else "<奥黛丽·刘·伊西娅·亦菲·赫本·庭华>"
            elif response_data["gender"] == "1":
                nick_name = f'帅哥<{response_data["name"]}>'
            else:
                nick_name = f'<{response_data["name"]}>'
            logging.info(f'[{get_now()}] {nick_name}，登录成功！')
            self.uid = response_data["org_score_info"]["uid"]
        else:
            logging.error(f'[{get_now()}] 登录失败，程序退出，请检查config.json中账号和密码！')
            exit(-1)


    def search_seat(self):
        data = {
            "beginTime" : self.start_time,
            "duration" : self.duration,
            "num" : 1,
            "space_category[category_id]" : self.category_id,
            "space_category[content_id]" : self.content_id
        }

        try:
            response = self.session.post(self.urls['search_seat'], data=data, headers=self.fake_header)
        except requests.exceptions.ReadTimeout:
            logging.error(f'[{get_now()}] search_seat页面超时无响应')
            exit(-1)
        
        if response.status_code == 200:
            response_data = response.json()
            # seat_id==0 听从系统推荐
            if self.seat_id == 0:
                self.target_seat = response_data["data"]["bestPairSeats"]["seats"][0]["id"]
                self.target_seat_title = response_data["data"]["bestPairSeats"]["seats"][0]["title"]
            # seat_id!=0 选择距离目标座位最近的一个座位
            else:
                min_abs = 1e10 # 初始值inf
                for seat in response_data["data"]["POIs"]:
                    # 筛选出可选的位置中，距离目标座位最近的一个
                    if seat['state'] == 0 or seat['state'] == 2:
                        # state=0表示可选，state=2表示推荐
                        cur_abs = abs(int(seat['title']) - self.seat_id)
                        if cur_abs < min_abs:
                            min_abs = cur_abs
                            self.target_seat = seat['id']
                            self.target_seat_title = seat['title']
            logging.info(f'[{get_now()}] 不错不错，座位#{self.target_seat_title} 可选！')
        else:
            logging.error(f'[{get_now()}] GG，没座位选')
            exit(-1)
    

    def book_seat(self):
        data = {
            "beginTime" : self.start_time,
            "duration" : self.duration,
            "seats[0]" : self.target_seat,
            "seatBookers[0]" : self.uid
        }

        try:
            response = self.session.post(self.urls['book_seat'], data=data, headers=self.fake_header)
            response_data = response.json()
        except requests.exceptions.ReadTimeout:
            logging.error(f'[{get_now()}] book_seat页面超时无响应')
            exit(-1)

        if response_data["CODE"] == "ok":
            logging.info(f'[{get_now()}] 估计不出意外是抢上宝座了！')
        else:
            logging.error(f'[{get_now()}] GG，预约失败')
            exit(-1)
    

    def get_my_booking_list(self):
        try:
            response = self.session.get(self.urls['get_my_booking_list'], headers=self.fake_header)
            response_data = response.json()
        except requests.exceptions.ReadTimeout:
            logging.error(f'[{get_now()}] get_my_booking_list页面超时无响应')
            exit(-1)
        
        if response_data["content"]["defaultItems"][0]["status"] != "0":
            logging.error(f'[{get_now()}] GG，好像没约上')
            exit(-1)
        
        start_timestamp = int(response_data["content"]["defaultItems"][0]["time"])
        duration_sec = int(response_data["content"]["defaultItems"][0]["duration"])
        start_timestr = time.strftime("%m月%d日%H:%M", time.localtime(start_timestamp))
        end_timestr = time.strftime("%H:%M", time.localtime(start_timestamp + duration_sec))
        seat_num = response_data["content"]["defaultItems"][0]["seatNum"]
        room_name = response_data["content"]["defaultItems"][0]["roomName"]
        logging.info(f'[{get_now()}] 已预约！<{start_timestr}到{end_timestr}>在<{room_name}>的<{seat_num}号>座位自习，记得签到！')


if __name__ == "__main__":
    logging.info("\n--------欢迎使用图书馆自助订座系统  版权所有:YiqinXiong--------")
    seat_booker = SeatBooker()
    seat_booker.login()
    seat_booker.search_seat()
    seat_booker.book_seat()
    seat_booker.get_my_booking_list()
