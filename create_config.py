from tkinter import *
from tkinter import ttk, messagebox
from json import dump as json_dump
import os

content_id_map = {
    '二楼南自习室(201)' : 36,
    '二楼北自习室(202)' : 35,
    '三楼南自习室(301)' : 31,
    '三楼北自习室(302)' : 37
}
 
if __name__ == '__main__':
    root = Tk()
    root.title("gua的抢座位神器")
    root.geometry("360x240")

    # 学号
    username_label = Label(root, text='学号：')
    username_label.grid(row=0, column=0)
    username = Entry(root, width=25)
    username.grid(row=0, column=1, padx=10, pady=5)
    # 密码
    password_label = Label(root, text='密码：')
    password_label.grid(row=1, column=0)
    password = Entry(root, show='*', width=25)
    password.grid(row=1, column=1, padx=10, pady=5)
    # 自习室
    room_label = Label(root, text='自习室：')
    room_label.grid(row=2, column=0)
    room = ttk.Combobox(root, width=22)
    room['value'] = ('二楼南自习室(201)', '二楼北自习室(202)', '三楼南自习室(301)', '三楼北自习室(302)')
    room['state'] = 'readonly'
    room.current(0)
    room.grid(row=2, column=1, padx=10, pady=5)
    # 开始时间
    start_time_label = Label(root, text='开始时间：')
    start_time_label.grid(row=3, column=0)
    start_time = ttk.Combobox(root, width=22)
    start_time['value'] = tuple(f'{x}:00' for x in range(7, 20))
    start_time['state'] = 'readonly'
    start_time.current(2)
    start_time.grid(row=3, column=1, padx=10, pady=5)
    # 持续时间
    duration_label = Label(root, text='开始时间：')
    duration_label.grid(row=4, column=0)
    duration = ttk.Combobox(root, width=22)
    duration['value'] = tuple(f'{x} 小时' for x in range(3, 16))
    duration['state'] = 'readonly'
    duration.current(10)
    duration.grid(row=4, column=1, padx=10, pady=5)
    # 预期座位号
    seat_id_label = Label(root, text='预期座位号（0表示随机）：')
    seat_id_label.grid(row=5, column=0)
    seat_id = Entry(root, width=25)
    seat_id.insert(0, "0")
    seat_id.grid(row=5, column=1, padx=10, pady=5)
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
            }
            print(config_map)
            with open('config.json', 'w') as fp:
                json_dump(config_map, fp)
        except ValueError:
            messagebox.showerror('错误', '输入了非数字，程序退出')
        finally:
            root.quit()
    button = Button(root, text='保存配置', command=save, width=10).grid(row=6, column=1, sticky=W)

    mainloop()