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
pageScreenShot = 'loginPage.png'
currentPath = os.path.dirname(os.path.abspath(__file__))
captPath = os.path.join(currentPath, captchaFileName)
logfilePath = os.path.join(currentPath, "sport.log")


def captcha_rec(captcha: Image):
    captcha = captcha.resize((100, 40))
    imgByteArr = BytesIO()
    captcha.save(imgByteArr, format='png')
    imgByteArr = imgByteArr.getvalue()
    files = {'image': imgByteArr}
    req = requests.post('https://plus.sjtu.edu.cn/captcha-solver/',
                        files=files)
    return json.loads(req.text)['result']


class SJTUSport(object):
    def __init__(self,
                 deltaDays=7,
                 venue='子衿街学生活动中心',
                 venueItem='健身房',
                 startTime=20):
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Firefox(options=self.options)
        self.driver.get('https://sports.sjtu.edu.cn')
        self.usr = account['username']
        self.psw = account['password']
        self.targetDate = datetime.datetime.now() + datetime.timedelta(
            deltaDays)
        self.venue = venue
        self.venueItem = venueItem
        self.startTime = startTime
        assert (self.driver.title == '上海交通大学体育场馆预约平台')
        logging.info("=================================")
        logging.info("SJTUSport initialize successfully")

    def login(self):
        """
        login without cookies
        """
        try:
            btn = self.driver.find_element_by_css_selector(
                '#app #logoin button')
            btn.click()
            while self.driver.title != '上海交通大学体育场馆预约平台':
                userInput = self.driver.find_element_by_id('user')
                userInput.send_keys(self.usr)
                passwdInput = self.driver.find_element_by_id('pass')
                passwdInput.send_keys(self.psw)
                self.driver.get_screenshot_as_file(pageScreenShot)
                captcha = self.driver.find_element_by_id('captcha-img')
                left = captcha.location['x']
                top = captcha.location['y']
                right = left + captcha.size['width']
                bottom = top + captcha.size['height']
                im = Image.open(pageScreenShot)
                im = im.crop((left, top, right, bottom))
                # Get the captcha by cropping the website screenshot
                # 在非headless模式下，若显示器进行了缩放将会出现错误
                im.save(captchaFileName)
                captchaVal = captcha_rec(im)
                logging.info("Captcha value: " + captchaVal)
                userInput = self.driver.find_element_by_id('captcha')
                userInput.send_keys(captchaVal)
                btn = self.driver.find_element_by_id('submit-button')
                btn.click()
                sleep(1)
            # print(self.driver.get_cookies())
            return 1
        except Exception as e:
            logging.error(str(e))
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
        seatId = self.startTime - 7
        btn = self.driver.find_elements_by_class_name('inner-seat')[seatId]
        btn.click()

    def order(self):
        try:
            self.searchAndEnterVenue()
            self.chooseVenueItemTab()
            self.chooseDateTab()
            self.chooseStartTime()

            # confirm order
            btn = self.driver.find_element_by_class_name('is-round')
            btn.click()

            # process notice
            btn = self.driver.find_element_by_class_name('el-checkbox__inner')
            btn.click()
            btn = self.driver.find_elements_by_class_name('btnStyle')[1]
            btn.click()

            # pay and commit
            btn = self.driver.find_element_by_class_name('is-round')
            btn.click()

            btn = self.driver.find_elements_by_css_selector(
                '.el-dialog__wrapper .el-button--primary')[0]
            btn.click()
            return 1
        except ElementNotInteractableException:
            logging.error("No seats left for " + self.venue + "-" +
                          self.venueItem + " at " + str(self.startTime) +
                          ":00 on " + self.targetDate.strftime('%Y-%m-%d'))
        except Exception as e:
            logging.error(str(e))
            return 0


logging.basicConfig(
    filename=logfilePath,
    level='INFO',
    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
)
logging.info("Log Started")

if __name__ == "__main__":
    sport = SJTUSport(startTime=20, venue='子衿街学生活动中心', venueItem='健身房')
    if sport.login() == 1:
        print("Login successfully!")
        logging.info("Login successfully")
    else:
        os._exit(0)
    if sport.order() == 1:
        print("Order successfully!")
        logging.info("Order successfully")
    else:
        os._exit(0)
