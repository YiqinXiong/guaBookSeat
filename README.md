# guaBookSeat
LTH的图书馆预约机，用于JXNU的图书馆座位预约。

很简单的抓包 + python requests库实现。

### 用法

```shell
# 依赖第三方库 requests
pip3 install requests==2.27.1

# 克隆本仓库
git clone https://github.com/YiqinXiong/guaBookSeat.git
cd ./guaBookSeat

# 创建配置文件
python3 create_config.py

# （可选）手动进行一次预约
python3 guaBookSeat.py

# （可选）加入crontab，每天22:00过后自动预约
sudo crontab -e # 编辑crontab任务
1 22 * * * /usr/local/bin/python3 /.../guaBookSeat/guaBookSeat.py	# 每天22:01执行一次预约任务，此处python和脚本都需用绝对路径
sudo crontab -l # 查看crontab任务
```

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



