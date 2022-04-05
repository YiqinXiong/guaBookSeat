import os
from tkinter import *
from tkinter import ttk, messagebox
from json import dump as json_dump
from my_tool import parent_dir_name, load_json_conf

content_id_map = {
    '二楼南自习室(201)' : 36,
    '二楼北自习室(202)' : 35,
    '三楼南自习室(301)' : 31,
    '三楼北自习室(302)' : 37
}
 
if __name__ == '__main__':
    # 如果已有配置文件则读取原配置
    conf = load_json_conf()
    if not conf:
        print("无配置文件，重新生成")

    root = Tk()
    root.title("gua的抢座位神器")
    root.geometry("400x240+600+300")
    root.resizable(0, 0)

    entry_width = 18
    combobox_width = 15
    short_combo_width = 9

    # 学号
    username_label = Label(root, text='学号：')
    username_label.grid(row=0, column=0)
    username = Entry(root, width=entry_width)
    if conf:
        username.insert(0, conf['username'])
    username.grid(row=0, column=1, pady=5)
    # 密码
    password_label = Label(root, text='密码：')
    password_label.grid(row=1, column=0)
    password = Entry(root, show='*', width=entry_width)
    if conf:
        password.insert(0, conf['password'])
    password.grid(row=1, column=1, pady=5)
    # 自习室
    room_label = Label(root, text='自习室：')
    room_label.grid(row=2, column=0)
    room = ttk.Combobox(root, width=combobox_width)
    room['value'] = ('二楼南自习室(201)', '二楼北自习室(202)', '三楼南自习室(301)', '三楼北自习室(302)')
    room['state'] = 'readonly'
    room.current(0)
    if conf:
        room.current(
            [x for x in range(len(content_id_map)) if list(content_id_map.values())[x]==conf['content_id']][0]
        )
    room.grid(row=2, column=1, pady=5)
    # 开始时间
    start_time_label = Label(root, text='开始时间：')
    start_time_label.grid(row=3, column=0)
    start_time = ttk.Combobox(root, width=combobox_width)
    start_time['value'] = tuple(f'{x}:00' for x in range(7, 20))
    start_time['state'] = 'readonly'
    start_time.current(2)
    if conf:
        start_time.current(conf['start_time']-7)
    start_time.grid(row=3, column=1, pady=5)
    # 开始时间波动
    start_time_delta_label = Label(root, text='容许误差：')
    start_time_delta_label.grid(row=3, column=2)
    start_time_delta = ttk.Combobox(root, width=short_combo_width)
    start_time_delta['value'] = tuple(f'前后 {x} 小时' for x in range(0, 5))
    start_time_delta['state'] = 'readonly'
    start_time_delta.current(2)
    if conf:
        start_time_delta.current(conf['start_time_delta'])
    start_time_delta.grid(row=3, column=3, pady=5)
    # 持续时间
    duration_label = Label(root, text='持续时间：')
    duration_label.grid(row=4, column=0)
    duration = ttk.Combobox(root, width=combobox_width)
    duration['value'] = tuple(f'{x} 小时' for x in range(3, 16))
    duration['state'] = 'readonly'
    duration.current(10)
    if conf:
        duration.current(conf['duration']-3)
    duration.grid(row=4, column=1, pady=5)
    # 持续时间波动
    duration_delta_label = Label(root, text='容许误差：')
    duration_delta_label.grid(row=4, column=2)
    duration_delta = ttk.Combobox(root, width=short_combo_width)
    duration_delta['value'] = tuple(f'前后 {x} 小时' for x in range(0, 7))
    duration_delta['state'] = 'readonly'
    duration_delta.current(4)
    if conf:
        duration_delta.current(conf['duration_delta'])
    duration_delta.grid(row=4, column=3, pady=5)
    # 预期座位号
    seat_id_label = Label(root, text='预期座号(0:随机)：')
    seat_id_label.grid(row=5, column=0)
    seat_id = Entry(root, width=entry_width)
    if conf:
        seat_id.insert(0, str(conf['seat_id']))
    else:
        seat_id.insert(0, "0")
    seat_id.grid(row=5, column=1, pady=5)
    # 保存按钮
    def save():
        if username.get() == "" or password.get() == "":
            messagebox.showwarning('警告', '用户名和密码不能为空')
            return
        try:
            config_map = {
                'username': username.get(),
                'password': password.get(),
                'content_id': content_id_map[room.get()],
                'start_time': int(start_time.get().split(':')[0]),
                'duration': int(duration.get().split(' ')[0]),
                'seat_id': int(seat_id.get()),
                'category_id': 591,
                'start_time_delta': int(start_time_delta.get().split(' ')[1]),
                'duration_delta': int(duration_delta.get().split(' ')[1]),
            }
            print(config_map)
            with open(os.path.join(parent_dir_name, "config.json"), 'w') as fp:
                json_dump(config_map, fp)
        except ValueError:
            messagebox.showerror('错误', '输入了非数字，程序退出')
        finally:
            root.quit()
    button = Button(root, text='保存配置', command=save, width=short_combo_width, pady=5).grid(row=6, column=1)

    mainloop()