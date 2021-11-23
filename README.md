# jAutoVenue

基于python selenium实现的<del> 低鲁棒性的、可靠性不保证的 </del>自用一键预约交大体育场馆脚本。

### 实现动机
在pc端进行交大体育场馆预约的过程略显繁琐，需要处理许多确认信息，适逢本人最近在学习selenium库的使用，因此，决定以一键预约交大体育场馆为目标进行python环境中selenium的实践。

### 实现思路
利用selenium，在[上海交通大学体育场馆预约平台](https://sports.sjtu.edu.cn/)页面上，利用id、class、css来定位元素，并进行文字输入、按钮点击等一系列操作，实现对人工预约流程的模拟。由于支付过程将涉及与微信/支付宝的对接，较为繁琐，与本脚本一键预约的目的相违背。因此，该脚本目前认定使用者在预约系统的零钱包中有充足的余额完成场馆预订（事实上，可以通过事先同时预定多个场馆而后退订来达到向预约系统充值的目的）。

### 环境要求
python 3，selenium库，与浏览器对应的webDriver(代码中使用的是firefox，可任意替换为edge、chrome)。

### 使用方式
在config.py中设定个人的jaccount账号与密码，通过命令行参数与sport.py交互即可查看使用说明，或者设定具体场馆、细分项目、日期、时间，进而实现一键预约。
```bash
>>> python3 sport.py --help
sport.py -d <delta days from today ranging from 0 to 7 > -i <venue item name> -t <startTime ranging from 7 to 21 > -v <venue name>
or: sport.py --day=<delta days from today ranging from 0 to 7 > --item=<venue item name> --time=<startTime ranging from 7 to 21 > --venue=<venue name>
venue-venueItem list:
子衿街学生活动中心: { 舞蹈, 健身房, 棋牌室, 钢琴, 烘焙, 琴房兼乐器, }
学生服务中心: { 台球, 健身房, }
徐汇校区体育馆: { 健身房, 羽毛球, 乒乓球, }
气膜体育中心: { 羽毛球, 篮球, }
南区体育馆: { 乒乓球, 排球, 篮球, }
胡法光体育场: { 舞蹈, }
霍英东体育中心: { 羽毛球, 篮球, 健身房, }
致远游泳馆东侧足球场: { 足球, }
笼式足球场: { 足球, }
子衿街南侧网球场: { 网球, }
东区网球场: { 网球, }

>>> python3 sport.py -d 6 -t 20 -v 子衿街学生活动中心 -i 健身房
SJTUSport initialize successfully
Captcha value: nsgr
Login successfully
Order committed: 子衿街学生活动中心-健身房 at 20:00 on 20XX-XX-XX
Order successfully

>>> python3 sport.py -d 5 -t 7 -v 子衿街学生活动中心 -i 钢琴
SJTUSport initialize successfully
Captcha value: fmfkk
Login successfully
No seats left in 子衿街学生活动中心-钢琴 at 7:00 on 20XX-XX-XX
```

### 注
该程序为本人学习selenium心血来潮之作，仅供学习使用，不保证运行效率与准确性。
