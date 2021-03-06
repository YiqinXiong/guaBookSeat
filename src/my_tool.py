import os, sys
import time
import datetime
from json import load as json_load

parent_dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_start_time(conf_start_time):
    # 获取今日0点时间戳
    now_hour = datetime.datetime.now().hour
    today = datetime.date.today()
    today_timestamp = int(time.mktime(today.timetuple()))
    # 若今日未到22:00，则预约今日自习室，否则预约明日自习室
    return (today_timestamp + 3600*conf_start_time) if now_hour < 22 else (today_timestamp + 86400 + 3600*conf_start_time)

def get_start_end_timestr(start_time, duration):
    start_timestr = time.strftime("%m-%d %H:%M", time.localtime(start_time))
    end_timestr = time.strftime("%H:%M", time.localtime(start_time + duration))
    return start_timestr, end_timestr

def load_json_conf():
    # 读取config
    try:
        with open(os.path.join(parent_dir_name, "config.json"), 'r') as fp:
            conf = json_load(fp)
        return conf
    except FileNotFoundError:
        return None

def replace_python_path():
    python_path = f'\n{sys.executable} '
    # 修改mac端脚本
    try:
        with open(os.path.join(parent_dir_name, "mac-2-预约位置.command"), 'r') as fp:
            content = fp.read()
        content = content.replace('\npython3 ', python_path)
        with open(os.path.join(parent_dir_name, "mac-2-预约位置.command"), 'w') as fp:
            fp.write(content)
        return 0
    except FileNotFoundError:
        return -1

def replace_win_2_path_in_xml():
    new_command = f'<Command>{parent_dir_name}\\win-2-预约位置.bat</Command>'
    # 修改xml文件
    try:
        with open(os.path.join(parent_dir_name, "booking.xml"), 'r', encoding='gbk') as fp:
            content = fp.read()
        content = content.replace('<Command>E:\workspace\guaBookSeat\win-2-预约位置.bat</Command>', new_command)
        with open(os.path.join(parent_dir_name, "booking.xml"), 'w', encoding='gbk') as fp:
            fp.write(content)
        return 0
    except FileNotFoundError:
        return -1

