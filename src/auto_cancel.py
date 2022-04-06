from my_tool import load_json_conf
from guaBookSeat import SeatBooker, SeatBookerStatus


if __name__ == "__main__":
    # 导入配置
    conf = load_json_conf()
    if not conf:
        exit(-1)
    # 实例化
    seat_booker = SeatBooker(conf)
    # login过程
    res_login = seat_booker.loop_login(max_failed_time=3)
    if res_login == SeatBookerStatus.LOOP_FAILED:
        exit(-1)
    # cancel_booking过程
    seat_booker.cancel_booking()