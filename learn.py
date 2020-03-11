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
import traceback

from selenium import webdriver
import time
import re
import pyautogui
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

from allow_flash import allow_flash
import pickle
import random as r

from my_logger import MyLogger


class Learn:

    learn_store = {}
    learn_course = []
    current_course_index = 0
    current_training_index = 0
    current_training_store_file = 'current_training.pkl'
    question_titles = []
    answer_list = []
    browser = None

    def __init__(self, logger):
        self.url = 'http://hzcj.91cme.com/'
        self.current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        self.learn_config = configparser.ConfigParser()
        self.learn_config.read("learn_config.ini")

        self.user = self.learn_config.get("account", "user_name")
        self.pwd = self.learn_config.get("account", "password")
        self.current_page = 1
        self.learn_store = self.read_object(self.current_training_store_file)
        self.my_logger = logger

    def open_main_page(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--allow-outdated-plugins')
            args = ["hide_console"]
            self.browser = webdriver.Chrome('chromedriver.exe', service_args=args, options=chrome_options)
            allow_flash(self.browser, self.url)
            self.browser.maximize_window()
            self.browser.get(self.url)
            self.login_in()
            self.start_course()
        except Exception as e:
            self.my_logger.info(e.args)
            self.my_logger.info(traceback.format_exc())
            self.my_logger.info('学习异常停止，线程已经关闭')

    def start_course(self):
        """
        开始进入课程
        :return:
        """
        course = self.select_course()
        while course is not None:
            time.sleep(1)
            course.click()
            self.ready_to_read_video()
            self.show_course()
            course = self.select_course()

    def show_course(self):
        """
        展示课程
        :return:
        """
        time.sleep(5)
        self.browser.switch_to.default_content()
        time.sleep(1)
        self.browser.switch_to.frame('topFrame')
        navl_list = self.browser.find_elements_by_css_selector('#navul li')
        navl_list[3].click()
        time.sleep(1)
        self.browser.switch_to.default_content()

    def ready_to_read_video(self):
        """
        进入课件详细页面 >> 进入视频页面 >> 点击视频播放按钮
        :return:
        """
        self.into_trainning_info_page()
        if self.into_video_page() is False:
            self.my_logger.info('skip read video')
            self.return_to_training_list()
            return
        self.play_video()
        self.listen_video_end(0)
        # 视频看完了点返回
        self.return_to_training_info()
        # 视频看完了开始考试
        self.into_exam_page()

    def into_trainning_info_page(self):
        time.sleep(2)
        traning = self.select_traning()
        time.sleep(1)
        traning.click()

    def return_to_training_info(self):
        """从视频播放页面返回到课件详情页"""
        time.sleep(2)
        # todo 返回课件详情页有问题
        # return_btn = self.browser.find_element_by_css_selector('#return .btn_c')
        # return_btn.click()
        a_links = self.browser.find_elements_by_css_selector('.mt-tabpage-title a')
        if len(a_links) >= 4:
            a_links[3].click()

    def return_to_training_list(self):
        """从课件详情页面返回到课件列表页面"""
        time.sleep(3)
        # todo 返回课件详情页有问题
        # return_btn2 = self.browser.find_elements_by_css_selector('.tj_btn .btn_c')
        return_btn2 = self.browser.find_elements_by_css_selector('.tgks_title_c div')
        if len(return_btn2) >= 1:
            return_btn2[0].click()
        else:
            self.my_logger.info('Can not return course detail.')

    def listen_video_end(self, count):
        try:
            if count > 100:
                self.my_logger.info('listen more than 100 times')
            count = count + 1
            current_time = self.browser.find_element_by_css_selector('#getCurrentTime span')
            duration = self.browser.find_element_by_css_selector('#duration span')
            while duration.text != current_time.text:
                time.sleep(20)
                current_time = self.browser.find_element_by_css_selector('#getCurrentTime span')
                self.my_logger.info(current_time.text)
        except StaleElementReferenceException:
            self.listen_video_end(count)

    def play_video(self):
        time.sleep(10)
        js_top = "var q=document.documentElement.scrollTop=0"
        self.browser.execute_script(js_top)
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
        change_pwd_title = self.browser.find_elements_by_css_selector('.title_list_a a')
        if len(change_pwd_title) >= 1:  # 如果是要修改密码就返回直接登录
            self.browser.back()
            time.sleep(1)
            relogin_btn = self.browser.find_element_by_css_selector('.login_main .login_btn')
            relogin_btn.click()

    def select_course(self):
        time.sleep(3)
        self.browser.switch_to.frame('mainFrame')
        lis = self.browser.find_elements_by_css_selector('.trainingList li')
        for index, li in enumerate(lis):
            training = li.find_element_by_css_selector('.trainingPic')
            p_list = li.find_elements_by_css_selector('.training_infor p')
            self.my_logger.info("第{}个课程状态：{}".format(str(index), p_list[3].text))
            if '培训状态： 合格' == p_list[3].text:
                self.current_course_index = index
                return training
        return None

    def select_traning(self):
        time.sleep(5)
        tbody_list = self.browser.find_elements_by_css_selector('table tbody')
        self.my_logger.info(tbody_list)
        tr_list = tbody_list[2].find_elements_by_css_selector('tr')
        for index, tr in enumerate(tr_list):
            td_list = tr.find_elements_by_css_selector('td')
            # try:
            #     if self.current_course_index in self.learn_store and index in self.learn_store[self.current_course_index]:
            #         continue
            # except KeyError:
            #     print('{} is not it finished store'.format(str(index)))
            if td_list[5].text == '未完成':
                self.my_logger.info('第{}是未完成'.format(str(index+1)))
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
        # 如果视频已经看完了，看下需不需要考试
        self.into_exam_page()
        return False

    def into_exam_page(self):
        """
        进入考试界面
        :param btn:
        :return:
        """
        time.sleep(3)
        try:
            home_work = self.browser.find_element_by_xpath("//input[@id='button2']/../..").find_element_by_css_selector(
                '.zt_red')
        except :
            self.my_logger.info('已经完成作业')
            return
        if '参加练习' in home_work.text:
            self.my_logger.info('视频未看完')
        if '参加考试' in home_work.text:
            home_work.click()
            self.start_exam()

    def start_exam(self):
        """
        开始考试
        :return:
        """
        time.sleep(5)
        self.browser.switch_to.frame('frameExam')
        self.answer_the_question()
        self.find_true_answers()
        retry_success = self.retry_answer_the_question()
        if retry_success is False:
            return
        self.apply_hours()


    def apply_hours(self):
        """
        申请学时
        :return:
        """
        time.sleep(3)
        applay_btn = self.browser.find_element_by_css_selector('.tgks_content .tgks_title_c div')
        if '立即申请学时' in applay_btn.text:
            applay_btn.click()
            self.confirm_alert()

    def find_true_answers(self):
        time.sleep(2)
        ques_infos = self.browser.find_elements_by_css_selector('.ques_info')
        self.question_titles.clear()
        self.answer_list.clear()
        for index, ques_info in enumerate(ques_infos):
            question_title = ques_info.find_element_by_css_selector('.ksts_title1 span').text  # 题目
            question_answers = ques_info.find_elements_by_css_selector('#ques_key span')  # 选择 'A.  低度风险区域'、'B.  中度风险区域'、'C.  重度风险区域'、'D.  无风险区域'
            question_answer_true = ques_info.find_elements_by_css_selector('#ques_result #ques_result_true')[1].text  # '正确答案: C'
            answer_true = re.findall('正确答案: ([a-zA-Z]{1})', question_answer_true)
            answer_true_index = ['A', 'B', 'C', 'D'].index(answer_true[0])
            self.question_titles.append(question_title)
            self.answer_list.append(answer_true_index)
        self.my_logger.info("question titles is : {}".format(self.question_titles))
        self.my_logger.info("anser is : {}".format(self.answer_list))

    def answer_the_question(self):
        """
        随机回答问题
        :return:
        """
        time.sleep(2)
        q_list = self.browser.find_elements_by_css_selector('#questionName div')  # 问题列表
        for question in q_list:
            time.sleep(r.randint(3, 10))
            answers = question.find_elements_by_css_selector('ul .questionContent')
            answer_index = r.randint(0, len(answers) - 1)
            answers[answer_index].find_element_by_css_selector('input').click()  # 随机选一个答案
        self.browser.find_element_by_css_selector('#tijiao').click()  # 提交
        self.confirm_alert()

    def retry_answer_the_question(self):
        """
        有了答案后重新答题
        :return:
        """
        time.sleep(2)
        retry_btn = self.browser.find_element_by_xpath("//input[@value='重新答题']")
        retry_btn.click()
        time.sleep(5)
        try:
            self.browser.switch_to.frame('frameExam')
        except:
            self.my_logger.info('重做切换失败')
        q_list = self.browser.find_elements_by_css_selector('#questionName div')  # 问题列表
        if len(self.question_titles) != len(q_list):
            self.my_logger.info('the answer is not right.')
            return False
        for index, question in enumerate(q_list):
            time.sleep(r.randint(3, 10))
            answers = question.find_elements_by_css_selector('ul .questionContent')
            answer_index = self.answer_list[index]
            answers[answer_index].find_element_by_css_selector('input').click()  # 随机选一个答案
        self.browser.find_element_by_css_selector('#tijiao').click()  # 提交
        self.confirm_alert()
        return True

    def confirm_alert(self):
        """
        确认alert
        :return:
        """
        time.sleep(2)
        ale = self.browser.switch_to.alert  # alert 确定
        self.my_logger.info(ale.text)
        ale.accept()

    def inspect_video_study_status(self, btns):
        """
        检查视频是否已经学习过了，如果学习过了存储到 pkl 文件中
        :param btns:
        :return:
        """
        if btns[0].get_attribute('value') == '已学习':
            self.my_logger.info('{}.{} this already readed.'.format(self.current_course_index, self.current_training_index))
            # if self.current_course_index in self.learn_store:
            #     self.learn_store[self.current_course_index].append(self.current_training_index)
            # else:
            #     self.learn_store.update({self.current_course_index: [self.current_training_index]})
            # print(self.learn_store)
            # self.store_object(self.learn_store, self.current_training_store_file)
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





