# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import configparser
import os

from selenium import webdriver
import time
import re
import logging
import pyautogui
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

from allow_flash import allow_flash
import pickle

class Learn:

    learn_store = {}
    learn_course = []
    current_course_index = 0
    current_training_index = 0
    current_training_store_file = 'current_training.pkl'

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--allow-outdated-plugins')
        self.browser = webdriver.Chrome('chromedriver.exe', options=chrome_options)
        self.url = 'http://hzcj.91cme.com/'
        self.current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.learn_config = configparser.ConfigParser()
        self.learn_config.read("learn_config.ini")

        self.user = self.learn_config.get("account", "user_name")
        self.pwd = self.learn_config.get("account", "password")
        self.current_page = 1
        self.learn_store = self.read_object(self.current_training_store_file)

    def open_main_page(self):
        allow_flash(self.browser, self.url)
        self.browser.maximize_window()
        self.browser.get(self.url)
        self.login_in()
        self.start_course()

    def start_course(self):
        """
        开始进入课程
        :return:
        """
        course = self.select_course()
        time.sleep(1)
        course.click()
        while True:
            self.ready_to_read_video()

    def ready_to_read_video(self):
        """
        进入课件详细页面 >> 进入视频页面 >> 点击视频播放按钮
        :return:
        """
        self.into_trainning_info_page()
        if self.into_video_page() is False:
            print('skip read video')
            self.return_to_training_list()
            return
        self.play_video()
        self.listen_time(0)
        # 视频看完了点返回
        self.return_to_training_info()
        time.sleep(5)
        self.return_to_training_list()

    def into_trainning_info_page(self):
        traning = self.select_traning()
        time.sleep(1)
        traning.click()

    def return_to_training_info(self):
        """从视频播放页面返回到课件详情页"""
        return_btn = self.browser.find_element_by_css_selector('#return .btn_c')
        return_btn.click()

    def return_to_training_list(self):
        """从课件详情页面返回到课件列表页面"""
        return_btn2 = self.browser.find_elements_by_css_selector('.tj_btn .btn_c')
        return_btn2[1].click()

    def listen_time(self, count):
        try:
            if count > 100:
                print('listen more than 100 times')
            count = count + 1
            current_time = self.browser.find_element_by_css_selector('#getCurrentTime span')
            duration = self.browser.find_element_by_css_selector('#duration span')
            while duration.text != current_time.text:
                time.sleep(20)
                current_time = self.browser.find_element_by_css_selector('#getCurrentTime span')
                print(current_time.text)
        except StaleElementReferenceException:
            self.listen_time(count)

    def play_video(self):
        time.sleep(10)
        x_str = self.learn_config.get("screen", "x")
        y_str = self.learn_config.get("screen", "y")
        pyautogui.click(x=float(x_str), y=float(y_str), clicks=1, interval=0.0, button='left')

    def login_in(self):
        user = self.browser.find_element_by_id('txtLogonUserCode')
        pwd = self.browser.find_element_by_id('txtLogonPassword')
        time.sleep(1)
        user.clear()
        user.send_keys(self.user)
        time.sleep(1)
        pwd.clear()
        pwd.send_keys(self.pwd)
        login_btn = self.browser.find_element_by_css_selector('.login_btn')
        time.sleep(1)
        login_btn.click()

    def select_course(self):
        self.browser.switch_to.frame('mainFrame')
        lis = self.browser.find_elements_by_css_selector('.trainingList li')
        for index, li in enumerate(lis):
            training = li.find_element_by_css_selector('.trainingPic')
            p_list = li.find_elements_by_css_selector('.training_infor p')
            print("第{}个课程状态：{}".format(str(index), p_list[3].text))
            if '培训状态： 未合格' == p_list[3].text:
                self.current_course_index = index
                return training
        return None

    def select_traning(self):
        time.sleep(5)
        tbody_list = self.browser.find_elements_by_css_selector('table tbody')
        print(tbody_list)
        tr_list = tbody_list[2].find_elements_by_css_selector('tr')
        for index, tr in enumerate(tr_list):
            td_list = tr.find_elements_by_css_selector('td')
            try:
                if self.current_course_index in self.learn_store and index in self.learn_store[self.current_course_index]:
                    continue
            except KeyError:
                print('{} is not it finished store'.format(str(index)))
            if td_list[5].text == '未完成':
                print('第{}是未完成'.format(str(index+1)))
                study_link = td_list[7].find_element_by_css_selector('a')
                self.current_training_index = index
                return study_link
        return None

    def into_video_page(self):
        time.sleep(2)
        btns = self.browser.find_elements_by_css_selector('table tbody tr #button2')
        bol = self.inspect_video_study_status(btns)
        if bol is True:
            btns[0].click()
            return True
        return False

    def inspect_video_study_status(self, btns):
        """
        检查视频是否已经学习过了，如果学习过了存储到 pkl 文件中
        :param btns:
        :return:
        """
        if btns[0].get_attribute('value') == '已学习':
            print('{}.{} this already readed.'.format(self.current_course_index, self.current_training_index))
            if self.current_course_index in self.learn_store:
                self.learn_store[self.current_course_index].append(self.current_training_index)
            else:
                self.learn_store.update({self.current_course_index: [self.current_training_index]})
            print(self.learn_store)
            self.store_object(self.learn_store, self.current_training_store_file)
            return False
        return True

    def store_object(self, obj, file_name):
        """
        存储数据到文件
        :param obj:
        :param file_name:
        :return:
        """
        with open(file_name, 'wb') as file_store:
            pickle.dump(obj, file_store)

    def read_object(self, file_name):
        """
        读取文件数据
        :param file_name:
        :return:
        """
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file_store:
                learn = pickle.load(file_store)
            return learn
        return {}


learn = Learn()
learn.open_main_page()


