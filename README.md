# guaBookSeat
LTH的图书馆预约机，用于JXNU的图书馆座位预约。

很简单的抓包 + python requests模块实现。

## 用法

### 前置条件

- 安装有Python3（如何检查？见下方）
  - Windows：按下`Win+S`，输入`cmd`打开命令提示符窗口，向窗口输入`python3 --version`，正常情况会出现版本信息，例如 `Python 3.9.12`
  - Mac：打开 `终端 (Terminal)`，在终端中输入`python3 --version`，正常情况会出现版本信息，例如 `Python 3.9.12`
- 安装第三方库 requests（安装方法？见下方）
  - Windows：命令提示符窗口输入 `pip3 install requests`
  - Mac：终端窗口输入 `pip3 install requests`
  - 若出现网络错误：尝试 `pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests`
- 下载本工具
  - Windows
    - 在右侧Release处下载 `guaBookSeat_Win.zip`即可
  - Mac：
    - `git clone https://github.com/YiqinXiong/guaBookSeat.git guaBookSeat_Mac`

### Windows用户

1. **解压 `guaBookSeat_Win.zip`，进入 `guaBookSeat_Win` 文件夹**

2. **按照下面的说明使用脚本文件，双击运行**

   | 脚本文件名                 | 功能                                                         | 注释                         |
   | -------------------------- | ------------------------------------------------------------ | ---------------------------- |
   | **win-1-修改参数.bat**     | 创建或修改配置（包括学号、密码、预约时间等）                 | 初次使用**务必先运行此脚本** |
   | **win-2-预约位置.bat**     | 按照配置文件的要求，开始预约位置                             | 相当于手动预约一次           |
   | **win-3-每日定时预订.bat** | 把 `win-2-预约位置.bat` 加入到Windows计划任务中，每天固定时间自动运行 | 固定时间默认为22:00          |
   | **win-4-取消定时预订.bat** | 取消固定时间自动运行 `win-2-预约位置.bat`                    |                              |

### Mac用户

1. **按照上文，克隆仓库到 `guaBookSeat_Mac` 文件夹**

2. **赋予脚本执行权限**

   1. 打开 `终端 (Terminal)`
   2. 在终端输入`cd`和`一个空格`，再将`git clone`得到的文件夹 `guaBookSeat_Mac`拖入终端，然后回车
   3. 继续输入`chmod +x mac*`，然后回车
   4. 关闭终端

3. **赋予crontab权限**

   1. 打开 `系统偏好设置 -> 安全性和隐私 -> 完全磁盘访问权限 `

   2. 解除锁定

   3. 点击 `+` 号

      <img src="https://xyq6785665.oss-cn-shenzhen.aliyuncs.com/img/1568979-20210906174234821-1959900899.png" alt="img" style="zoom: 50%;" />

   4. 按下快捷键组合`command + shift + G`，在弹出窗口输入框输入`/usr/sbin`，并选择打开

   5. 选择cron，点击打开

      <img src="https://xyq6785665.oss-cn-shenzhen.aliyuncs.com/img/1568979-20210906174258646-892103332.png" alt="img" style="zoom:50%;" />

   6. 保存设置并退出

4. **进入 `guaBookSeat_Mac` 文件夹**

5. **按照下面的说明使用脚本文件，双击运行**

   | 脚本文件名                     | 功能                                                         | 注释                         |
   | ------------------------------ | ------------------------------------------------------------ | ---------------------------- |
   | **mac-1-修改参数.command**     | 创建或修改配置（包括学号、密码、预约时间等）                 | 初次使用**务必先运行此脚本** |
   | **mac-2-预约位置.command**     | 按照配置文件的要求，开始预约位置                             | 相当于手动预约一次           |
   | **mac-3-每日定时预订.command** | 把 `mac-2-预约位置.command` 加入到crontab计划任务中，每天固定时间自动运行 | 固定时间默认为22:00          |
   | **mac-4-取消定时预订.command** | 取消固定时间自动运行 `mac-2-预约位置.command`                |                              |

## 额外说明

### 配置文件

使用 `python3 create_config.py` 创建配置文件后，同目录下会自动生成 `config.json` 文件，保存了登录信息等配置。

### 日志

运行脚本会自动打印日志到同目录下的 `guaBookSeat.log` 文件，可以查看脚本运行情况。

### crontab语法

```shell
*  *  *  *  *  <command>
```

1. 分钟，取值范围0-59

2. 小时，取值范围0-23

3. 几号，取值范围1-31

4. 月份，取值范围1-12

5. 星期几，取值范围0-7

6. 需要执行的命令，可以是语句或是脚本

#### 常用命令

```shell
crontab -e # 编辑crontab任务
crontab -l # 查看crontab任务
```

#### 示例1

```shell
* * * * * 上厕所
```

每分钟上一次厕所

#### 示例2

```shell
*/2 * * * * 上厕所
```

每2分钟上一次厕所

#### 示例3

```shell
1 */3 * * * 上厕所
```

每3小时的第1分钟上一次厕所

#### 示例4

```shell
1 3 * * * 上厕所
```

每天3点零1分上一次厕所

#### 示例5

```shell
*/20 6-12 * 12 * 上厕所
```

每年12月的每天早上6点到中午12点，每隔20分钟上一次厕所



