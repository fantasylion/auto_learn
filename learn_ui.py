#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys
from tkinter import StringVar, Tk

from learn import Learn

PythonVersion = 3
from tkinter.font import Font
from tkinter.ttk import *
from tkinter.messagebox import *

class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Form1')
        self.master.geometry('522x313')
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()

        self.style = Style()

        self.style.configure('Command1.TButton',font=('宋体',9))
        self.Command1 = Button(self.top, text='开始学习', command=self.Command1_Cmd, style='Command1.TButton')
        self.Command1.place(relx=0.046, rely=0.102, relwidth=0.14, relheight=0.105)

        self.style.configure('Command1.TButton',font=('宋体',9))
        self.Command1 = Button(self.top, text='重新学习', command=self.Command1_Cmd, style='Command1.TButton')
        self.Command1.place(relx=0.23, rely=0.102, relwidth=0.14, relheight=0.105)

        self.style.configure('Frame1.TLabelframe',font=('宋体',9))
        self.Frame1 = LabelFrame(self.top, text='Frame1', style='Frame1.TLabelframe')
        self.Frame1.place(relx=0.031, rely=0.281, relwidth=0.937, relheight=0.693)

        self.Text1Var = StringVar(value='我爱蓉蓉')
        self.Text1 = Entry(self.Frame1, text='Text1', textvariable=self.Text1Var, font=('宋体',9))
        self.Text1.place(relx=0.016, rely=0.074, relwidth=0.967, relheight=0.889)


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.learn = Learn()

    def Command1_Cmd(self, event=None):
        self.Text1Var = StringVar(value='开始学习')
        self.learn.open_main_page()
        pass

    def Command1_Cmd(self, event=None):
        self.learn.browser.close()
        self.Text1Var = StringVar(value='停止学习')
        pass

if __name__ == "__main__":
    top = Tk()
    Application(top).mainloop()
    try: top.destroy()
    except: pass
