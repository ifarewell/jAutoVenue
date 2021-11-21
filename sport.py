from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import *
from config import account
from SJTUVenueTabLists import venueTabLists
from PIL import Image
import requests
import os
import datetime
import logging
import json
from io import BytesIO
from time import sleep

captchaFileName = 'captcha.png'
currentPath = os.path.dirname(os.path.abspath(__file__))
captPath = os.path.join(currentPath, captchaFileName)
logfilePath = os.path.join(currentPath, "sport.log")


def captcha_rec(captcha: Image):
    '''
    SJTUPlus api only accepts captchas with size 100*40
    '''
    imgByteArr = BytesIO()
    captcha = captcha.resize((100, 40))
    captcha.save(imgByteArr, format='png')
    imgByteArr = imgByteArr.getvalue()
    files = {'image': imgByteArr}
    req = requests.post('https://plus.sjtu.edu.cn/captcha-solver/',
                        files=files)
    return json.loads(req.text)['result']


class SJTUSport(object):
    def __init__(self,
                 deltaDays: int=7,
                 venue: str='子衿街学生活动中心',
                 venueItem: str='健身房',
                 startTime: int=20):
        self.options = Options()
        self.options.headless = True
        self.options.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.get('https://sports.sjtu.edu.cn')
        self.usr = account['username']
        self.psw = account['password']
        self.targetDate = datetime.datetime.now() + datetime.timedelta(
            deltaDays)
        self.venue = venue
        self.venueItem = venueItem
        self.startTime = startTime
        assert self.driver.title == '上海交通大学体育场馆预约平台', 'Target site error.'
        logging.info("SJTUSport initialize successfully")
        print("SJTUSport initialize successfully")

    def login(self):
        try:
            btn = self.driver.find_element_by_css_selector(
                '#app #logoin button')
            btn.click()
            times = 0
            while self.driver.title != '上海交通大学体育场馆预约平台' and times < 10:
                times += 1
                warnInfo = self.driver.find_elements_by_id('div_warn')
                if len(warnInfo):
                    assert warnInfo[0].text != '请正确填写你的用户名和密码，注意：密码是区分大小写的', 'Please check config.py for your jaccount username and password.'
                    logging.error(warnInfo[0].text)
                    print(warnInfo[0].text)
                userInput = self.driver.find_element_by_id('user')
                userInput.send_keys(self.usr)
                passwdInput = self.driver.find_element_by_id('pass')
                passwdInput.send_keys(self.psw)

                # Get the captcha by cropping the website screenshot
                # If not in headless mode, zoom level should be set to 100%
                imgByteArr = self.driver.get_screenshot_as_png()
                captcha = self.driver.find_element_by_id('captcha-img')
                imgByteArr2 = BytesIO(imgByteArr)
                img = Image.open(imgByteArr2)
                left = captcha.location['x']
                top = captcha.location['y']
                right = left + captcha.size['width']
                bottom = top + captcha.size['height']
                img = img.crop((left, top, right, bottom))
                img.save(captchaFileName)
                captchaVal = captcha_rec(img)
                logging.info("Captcha value: " + captchaVal)
                print("Captcha value: " + captchaVal)
                userInput = self.driver.find_element_by_id('captcha')
                userInput.send_keys(captchaVal)
                btn = self.driver.find_element_by_id('submit-button')
                btn.click()
                sleep(1)
            # print(self.driver.get_cookies())
            assert times < 10, 'Something wrong with the captcha recognition process, please check the zoom params of your display device.'
            return 1
        except Exception as e:
            logging.error(str(e))
            print(str(e))
            return 0

    def searchAndEnterVenue(self):
        venueInput = self.driver.find_element_by_class_name('el-input__inner')
        venueInput.send_keys(self.venue)
        btn = self.driver.find_element_by_class_name('el-button--default')
        btn.click()
        sleep(1)

        btn = self.driver.find_element_by_class_name('el-card__body')
        btn.click()
        sleep(1)

    def chooseVenueItemTab(self):
        btn = self.driver.find_element_by_id(
            venueTabLists[self.venue][self.venueItem])
        btn.click()

    def chooseDateTab(self):
        dateId = 'tab-' + self.targetDate.strftime('%Y-%m-%d')
        btn = self.driver.find_element_by_id(dateId)
        btn.click()
        sleep(1)

    def chooseStartTime(self):
        """
        Start time ranges from 7 to 21
        """
        timeSlotId = self.startTime - 7
        chart = self.driver.find_element_by_class_name('chart')
        chart.screenshot('chart.png')
        wrapper = chart.find_element_by_class_name('inner-seat-wrapper')
        timeSlot = wrapper.find_elements_by_class_name('clearfix')[timeSlotId]
        seats = timeSlot.find_elements_by_class_name('unselected-seat')
        assert len(seats) > 0, "No seats left in " + self.venue + "-" +self.venueItem + " at " + str(self.startTime) +":00 on " + self.targetDate.strftime('%Y-%m-%d')
        seat = seats[0]
        seat.click()

    def order(self):
        try:
            self.searchAndEnterVenue()
            self.chooseVenueItemTab()
            self.chooseDateTab()
            self.chooseStartTime()

            # confirm order
            btn = self.driver.find_element_by_css_selector('.drawerStyle>.butMoney>.is-round')
            btn.click()

            # process notice
            btn = self.driver.find_element_by_css_selector('.dialog-footer>.tk>.el-checkbox>.el-checkbox__input>.el-checkbox__inner')
            btn.click()
            btn = self.driver.find_element_by_css_selector('.dialog-footer>div>.el-button--primary')
            btn.click()
            sleep(1)

            # pay and commit
            btn = self.driver.find_element_by_css_selector('.placeAnOrder>.right>.el-button--primary')
            btn.click()

            dialog = self.driver.find_element_by_css_selector('[aria-label="提示"]')
            btn = dialog.find_element_by_css_selector('.dialog-footer>.el-button--primary')
            btn.click()
            logging.info('Order committed: '+ self.venue + "-" +self.venueItem + " at " + str(self.startTime) +":00 on " + self.targetDate.strftime('%Y-%m-%d'))
            print('Order committed: '+ self.venue + "-" +self.venueItem + " at " + str(self.startTime) +":00 on " + self.targetDate.strftime('%Y-%m-%d'))
            return 1
        except Exception as e:
            logging.error(str(e))
            print(str(e))
            return 0

    def shutDown(self):
        self.driver.quit()

logging.basicConfig(
    filename=logfilePath,
    level='INFO',
    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
)
logging.info("=================================")
logging.info("Log Started")

if __name__ == "__main__":
    sport = SJTUSport(startTime=20, venue='子衿街学生活动中心', venueItem='健身房')
    if sport.login() == 1:
        logging.info("Login successfully")
        print("Login successfully!")
    else:
        sport.shutDown()
        os._exit(0)
    if sport.order() == 1:
        logging.info("Order successfully")
        print("Order successfully!")
    else:
        sport.shutDown()
        os._exit(0)
    sport.shutDown()