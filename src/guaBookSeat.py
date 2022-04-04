import os, sys
from sre_constants import SUCCESS
import requests
import logging
import time, datetime
from json import load as json_load
from enum import Enum
from random import randint

class SeatBookerStatus(Enum):
    SUCCESS = 1
    NO_SEAT = 2
    NOT_AFFORDABLE = 3
    STATUS_CODE_ERROR = 4
    TIME_OUT = 5
    PARAM_ERROR = 6
    UNKNOWN_ERROR = 7
    ALREADY_BOOKED = 8


parent_dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sh = logging.StreamHandler(sys.stdout)
fh = logging.FileHandler(os.path.join(parent_dir_name, "guaBookSeat.log"), encoding='utf-8')
logging.basicConfig(level=logging.INFO, handlers=[sh, fh])


def get_start_time(conf_start_time):
    # 获取今日0点时间戳
    now_hour = datetime.datetime.now().hour
    today = datetime.date.today()
    today_timestamp = int(time.mktime(today.timetuple()))
    # 若今日未到22:00，则预约今日自习室，否则预约明日自习室
    return (today_timestamp + 3600*conf_start_time) if now_hour < 22 else (today_timestamp + 86400 + 3600*conf_start_time)

def get_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def get_start_end_timestr(start_time, duration):
    start_timestr = time.strftime("%m-%d %H:%M", time.localtime(start_time))
    end_timestr = time.strftime("%H:%M", time.localtime(start_time + duration))
    return start_timestr, end_timestr


class SeatBooker():
    def __init__(self) -> None:
        try:
            with open(os.path.join(parent_dir_name, "config.json"), 'r') as fp:
                conf = json_load(fp)
        except FileNotFoundError:
            logging.error("无配置文件，请先使用“修改参数”脚本生成配置文件")
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
        except requests.exceptions.SSLError:
            logging.error(f'[{get_now()}] login页面post错误')
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
            return SeatBookerStatus.TIME_OUT
        
        if response.status_code == 200:
            response_data = response.json()
            start_timestr, end_timestr = get_start_end_timestr(self.start_time, self.duration)
            if "data" not in response_data.keys():
                logging.error(f'[{get_now()}] <{start_timestr}到{end_timestr}>在你选的教室没有符合条件的座位预约！')
                return SeatBookerStatus.NO_SEAT
            # 如果系统调整的时间太离谱，就不接受
            if "adjustDate" not in response_data["content"]["children"][1].keys():
                logging.error(f'{response_data["content"]["children"][1]}')
            valid_start_time = response_data["content"]["children"][1]["adjustDate"]
            valid_duration = response_data["content"]["children"][1]["adjustTime"]
            valid_start_timestr, valid_end_timestr = get_start_end_timestr(valid_start_time, valid_duration)
            logging.info(f'[{get_now()}] 预期<{start_timestr}到{end_timestr}>，调整后<{valid_start_timestr}到{valid_end_timestr}>')
            if abs(valid_start_time-self.start_time) > 3600 or abs(valid_duration-self.duration) > 3600:
                logging.error(f'[{get_now()}] 系统提出的调整不可接受！')
                return SeatBookerStatus.NOT_AFFORDABLE
            # 按照系统可用的时间更新预定时间
            self.start_time = valid_start_time
            self.duration = valid_duration
            # seat_id==0 听从系统推荐
            if self.seat_id == 0:
                self.target_seat = response_data["data"]["bestPairSeats"]["seats"][0]["id"]
                self.target_seat_title = response_data["data"]["bestPairSeats"]["seats"][0]["title"]
            # seat_id!=0 选择距离目标座位最近的一个座位，且最好是奇数
            else:
                min_abs = 1e10 # 初始值inf
                for seat in response_data["data"]["POIs"]:
                    cur_seat_title = int(seat['title'])
                    # 筛选出可选的位置中，距离目标座位最近的一个
                    if seat['state'] == 0 or seat['state'] == 2:
                        # state=0表示可选，state=2表示推荐
                        cur_abs = abs(cur_seat_title - self.seat_id)
                        if cur_abs < min_abs:
                            if min_abs-cur_abs>10 or cur_seat_title%2:
                                min_abs = cur_abs
                                self.target_seat = seat['id']
                                self.target_seat_title = seat['title']
            logging.info(f'[{get_now()}] 不错不错，座位#{self.target_seat_title} 可选！')
            return SeatBookerStatus.SUCCESS
        else:
            logging.error(f'[{get_now()}] GG，没座位选')
            return SeatBookerStatus.STATUS_CODE_ERROR
    

    def book_seat(self):
        data = {
            "beginTime" : self.start_time,
            "duration" : self.duration,
            "seats[0]" : self.target_seat,
            "seatBookers[0]" : self.uid
        }

        try:
            start_timestr, end_timestr = get_start_end_timestr(self.start_time, self.duration)
            logging.info(f'[{get_now()}] 发起订座申请{data["seats[0]"]}号，{start_timestr}到{end_timestr}')
            response = self.session.post(self.urls['book_seat'], data=data, headers=self.fake_header)
            response_data = response.json()
        except requests.exceptions.ReadTimeout:
            logging.error(f'[{get_now()}] book_seat页面超时无响应')
            return SeatBookerStatus.TIME_OUT

        if response_data["CODE"] == "ok":
            logging.info(f'[{get_now()}] 估计不出意外是抢上宝座了！')
            return SeatBookerStatus.SUCCESS
        elif response_data["CODE"] == "ParamError":
            logging.error(f'[{get_now()}] {response_data["MESSAGE"]}')
            if "已有预约" in response_data["MESSAGE"]:
                return SeatBookerStatus.ALREADY_BOOKED
            return SeatBookerStatus.PARAM_ERROR
        else:
            logging.error(f'[{get_now()}] GG，不明原因预约失败')
            return SeatBookerStatus.UNKNOWN_ERROR
    

    def get_my_booking_list(self):
        try:
            response = self.session.get(self.urls['get_my_booking_list'], headers=self.fake_header)
            response_data = response.json()
        except requests.exceptions.ReadTimeout:
            logging.error(f'[{get_now()}] get_my_booking_list页面超时无响应')
            return SeatBookerStatus.TIME_OUT
        
        if response_data["content"]["defaultItems"][0]["status"] != "0":
            logging.error(f'[{get_now()}] GG，好像没约上')
            return SeatBookerStatus.UNKNOWN_ERROR
        
        start_timestamp = int(response_data["content"]["defaultItems"][0]["time"])
        duration_sec = int(response_data["content"]["defaultItems"][0]["duration"])
        start_timestr, end_timestr = get_start_end_timestr(start_timestamp, duration_sec)
        seat_num = response_data["content"]["defaultItems"][0]["seatNum"]
        room_name = response_data["content"]["defaultItems"][0]["roomName"]
        logging.info(f'[{get_now()}] 已预约！<{start_timestr}到{end_timestr}>在<{room_name}>的<{seat_num}号>座位自习，记得签到！')
        return SeatBookerStatus.SUCCESS
    
    def adjust_conf_randomly(self, random_range=0, factor=1):
        border = round((random_range / 10) * 3600 * factor)
        start_time_lower_bound = get_start_time(7)  # 开始时间不早于7点
        start_time_upper_bound = get_start_time(19) # 开始时间不晚于19点
        duration_limit = 3600 * 3   # 至少保证3个小时的自习室

        self.start_time += round(randint(-border, border) / 3600) * 3600
        self.start_time = min(self.start_time, start_time_upper_bound)
        self.start_time = max(self.start_time, start_time_lower_bound)

        self.duration += round(randint(-2*border, border) / 3600) * 3600
        self.duration = max(self.duration, duration_limit)
        

if __name__ == "__main__":
    logging.info("\n--------欢迎使用图书馆自助订座系统  版权所有:YiqinXiong--------")
    seat_booker = SeatBooker()

    # login过程不允许重试
    seat_booker.login()

    # 总共尝试10次search_seat和book_seat的过程
    retry_time = 10
    while retry_time > 0:
        # 若search_seat失败可以循环重试，每2s一次，最多允许失败10次
        failed_time = 0
        res_search_seat = seat_booker.search_seat()
        while res_search_seat != SeatBookerStatus.SUCCESS:
            failed_time += 1
            # 失败10次以上退出search_seat流程
            if failed_time > 10:
                logging.error(f'[{get_now()}] search_seat已失败10次')
                break
            # 2秒重试
            time.sleep(2)
            # 无位置时大幅调整预定时间和时长
            if res_search_seat == SeatBookerStatus.NO_SEAT:
                seat_booker.adjust_conf_randomly(random_range=failed_time, factor=2.5)
            # 系统调整的时间不可接受时小幅调整预定时间和时长
            elif res_search_seat == SeatBookerStatus.NOT_AFFORDABLE:
                seat_booker.adjust_conf_randomly(random_range=failed_time, factor=1.5)
            res_search_seat = seat_booker.search_seat()
        # 若search_seat大失败，直接重新尝试一轮
        if res_search_seat != SeatBookerStatus.SUCCESS:
            continue
        # 若book_seat失败可以循环重试，每2s一次，最多允许失败3次
        failed_time = 0
        res_book_seat = seat_booker.book_seat()
        while res_book_seat != SeatBookerStatus.SUCCESS:
            failed_time += 1
            # 若已有预约，直接结束程序
            if res_book_seat == SeatBookerStatus.ALREADY_BOOKED:
                logging.info(f'[{get_now()}] 已有预约，程序结束')
                exit(0)
            # 失败3次以上退出程序
            if failed_time > 3:
                logging.error(f'[{get_now()}] book_seat已失败3次')
                break
            # 2秒重试
            time.sleep(2)
            res_book_seat = seat_booker.book_seat()
        # 若成功则可以跳出 retry 的大循环
        if res_book_seat == SeatBookerStatus.SUCCESS:
            break
        # 重试机会减少
        time.sleep(2)
        retry_time -= 1
        
    # 若get_my_booking_list失败可以循环重试，每2s一次，最多允许失败3次
    failed_time = 0
    res_get_my_booking_list = seat_booker.get_my_booking_list()
    while res_get_my_booking_list != SeatBookerStatus.SUCCESS:
        failed_time += 1
        # 失败3次以上退出get_my_booking_list流程
        if failed_time > 3:
            logging.error(f'[{get_now()}] get_my_booking_list已失败3次')
            break
        # 2秒重试
        time.sleep(2)
        res_get_my_booking_list = seat_booker.get_my_booking_list()
