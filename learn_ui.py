#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys
import threading
import time
from tkinter import Tk, END, NORMAL, DISABLED
from tkinter.scrolledtext import ScrolledText

from learn import Learn

from my_logger import MyLogger

PythonVersion = 3
from tkinter.ttk import *


class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('蓉蓉爱学习')
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        # 得到屏幕高度
        ww = 522
        wh = 313
        # 窗口宽高为100
        x = (sw - ww) / 2
        y = (sh - wh) / 2
        self.master.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
        self.log_board = None
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.style.configure('start_study.TButton',font=('宋体',9))
        self.start_study = Button(self.top, text='开始学习', command=self.start_study, style='start_study.TButton')
        self.start_study.place(relx=0.046, rely=0.102, relwidth=0.14, relheight=0.105)

        self.style.configure('stop_study.TButton',font=('宋体',9))
        self.stop_study = Button(self.top, text='停止学习', command=self.stop_study, style='stop_study.TButton')
        self.stop_study.place(relx=0.23, rely=0.102, relwidth=0.14, relheight=0.105)

        self.style.configure('clear_log.TButton',font=('宋体',9))
        self.clear_log = Button(self.top, text='清除日志', command=self.clear_log_Cmd, style='clear_log.TButton')
        self.clear_log.place(relx=0.414, rely=0.102, relwidth=0.14, relheight=0.105)

        self.style.configure('log_frame.TLabelframe',font=('宋体',9))
        self.log_frame = LabelFrame(self.top, text='学习日志', style='log_frame.TLabelframe')
        self.log_frame.place(relx=0.031, rely=0.281, relwidth=0.937, relheight=0.693)

        self.log_board = ScrolledText(self.log_frame, font=("宋体", 9))
        self.log_board.place(relx=0.016, rely=0.074, relwidth=0.967, relheight=0.889)
        self.log_board.insert(END, '我爱学习\n')

class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.logger = MyLogger(log_board=self.log_board, filename='all.log', level='debug')
        self.learn = Learn(self.logger)
        self.t1 = None

    def start_study(self, event=None):
        self.init_start_thread_ifnot()
        if self.t1.is_alive():
            self.logger.info('请不要重复学习')
            return
        try:
            self.t1.start()
        except:
            self.init_start_thread()
            self.t1.start()
        self.logger.info('已开始学习')
        pass

    def init_start_thread_ifnot(self):
        if self.t1 is None:
            self.init_start_thread()

    def init_start_thread(self):
        self.t1 = threading.Thread(target=self.learn.open_main_page)
        self.t1.daemon = True

    last_stop_time = None

    def do_stop_study(self):
        try:
            self.learn.browser.quit()
        except:
            self.logger.info('停止失败！，请重新停止')

        self.logger.info('已停止学习')

    def stop_study(self, event=None):
        if self.last_stop_time is not None:
            if (time.time() - self.last_stop_time) < 10:
                self.logger.info('太快了，请10秒后在点击')
                return
        if self.t1.is_alive() is False:
            self.logger.info('您没有在学习')
            return
        self.last_stop_time = time.time()
        self.logger.info('正在停止学习')
        close_t = threading.Thread(target=self.do_stop_study)
        close_t.daemon = True
        close_t.start()
        pass

    def clear_log_Cmd(self, event=None):
        self.log_board.config(state=NORMAL)
        self.log_board.delete('1.0', END)
        pass


if __name__ == "__main__":
    top = Tk()
    top.iconbitmap('C:\\DATA\\code\\auto_learn\\rr.ico')
    Application(top).mainloop()
    try: top.destroy()
    except: pass
