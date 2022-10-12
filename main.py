import base64
import json
import tkinter as tk
import traceback
from tkinter import ttk
from threading import Timer
from time import sleep
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showinfo, showwarning, showerror
import os
import requests
import js2py
from bs4 import BeautifulSoup
from urllib import parse

import yaml
from playwright.sync_api import sync_playwright


class Window:
    class GradeTableCrawler:
        def crawl(self) -> None:
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch(headless=self.is_headless.get())
                    page = browser.new_page()
                    page.goto(
                        "https://pass.jsu.edu.cn/#/UserLogin?sn=Uim4puN4SXeCCcZ0rD9rfg&client_id=Ah9e4vpCRMyT09OPMon4pA&redirect_uri=https%3A%2F%2Fi.jsu.edu.cn%2Fhome%2Fsimple")
                    page.get_by_placeholder("学工号").fill(self.stu_id.get())
                    page.get_by_placeholder("密码").fill(self.password.get())
                    page.get_by_role("button", name="立即登录").click()
                    page.wait_for_load_state(state='networkidle')
                    page.goto("https://kxdzpz.jsu.edu.cn/#/dashboard")
                    if "https://kxdzpz.jsu.edu.cn" not in page.url:
                        self.crawling_status = 2
                        browser.close()
                        return
                    page.get_by_role("link", name="成绩单").click()
                    page.wait_for_load_state(state='networkidle')
                    page.get_by_role("button", name="预览").click()
                    try:
                        with page.expect_download() as download_info:
                            sleep(4)
                            js = 'document.getElementById("the-canvas").toDataURL("image/png")'
                            img_base64 = page.evaluate(js)
                            msg = img_base64.split(',')[1]  # 去除前缀无用信息
                            self.image_data = base64.b64decode(msg)
                            self.crawling_status = 1
                            browser.close()
                    except:
                        self.crawling_status = 1
                        browser.close()
                except:
                    # traceback.print_exc()
                    self.crawling_status = 3
                    browser.close()
                    return

        def show_form_element(self):
            self.stu_id_label.place(x=160, y=159)
            self.stu_id_input.place(x=215, y=160)
            self.password_label.place(x=160, y=203)
            self.password_input.place(x=215, y=204)
            self.form_title_label.place(x=170, y=95)
            self.start_btn.place(x=105, y=280)
            self.cancel_btn.place(x=365, y=280)
            self.check_is_headless_btn.place(x=10, y=0)
            self.auto_login_btn.place(x=215, y=240)

        def hide_form_element(self):
            self.stu_id_label.place_forget()
            self.stu_id_input.place_forget()
            self.password_label.place_forget()
            self.password_input.place_forget()
            self.form_title_label.place_forget()
            self.start_btn.place_forget()
            self.cancel_btn.place_forget()
            self.check_is_headless_btn.place_forget()
            if hasattr(self, "auto_login_btn"):
                self.auto_login_btn.place_forget()

        def back_to_main(self):
            self.stu_id.set("")
            self.password.set("")
            self.hide_form_element()
            self.outer.show_element()

        def show_crawl_element(self):
            self.crawl_status_text.set(self.crawling_status_base_text)
            self.crawl_status_label.pack(expand='yes')
            self.crawl_cancel_btn.place(x=265, y=220)

        def hide_crawl_element(self):
            self.crawl_status_label.pack_forget()
            self.crawl_cancel_btn.place_forget()

        def crawl_monitor(self):
            if self.crawling_status == 0:
                self.crawl_status_dot_num = (self.crawl_status_dot_num + 1) % 4
                self.crawl_status_text.set(self.crawling_status_base_text + "." * self.crawl_status_dot_num)
                timer = Timer(1, self.crawl_monitor, ())
                timer.start()
            elif self.crawling_status == 1:
                self.crawl_status_text.set("获取成绩单成功")
                save_path = askdirectory()  # 使用askdirectory()方法返回文件夹的路径
                with open(save_path + "/我的成绩单.png", "wb") as f:
                    f.write(self.image_data)
                self.crawl_status_text.set("保存成绩单成功")
            elif self.crawling_status == 2:
                self.crawl_status_text.set("登录失败，请重试")
            elif self.crawling_status == 3:
                self.crawl_status_text.set("爬取被意外终止了")

        def start_crawl(self):
            self.hide_form_element()
            self.show_crawl_element()
            self.crawling_status = 0
            self.monitor_timer = Timer(1, self.crawl_monitor, ())
            self.monitor_timer.start()
            self.crawl_timer = Timer(0, self.crawl)
            self.crawl_timer.start()

        def back(self):
            self.crawling_status = 3
            if hasattr(self, "crawl_timer") and self.crawl_timer != None:
                self.crawl_timer.cancel()
                self.monitor_timer.cancel()
            self.stu_id.set("")
            self.password.set("")
            self.hide_crawl_element()
            self.show_form_element()

        def auto_login(self):
            self.get_config()
            if self.allow_auto_login:
                self.stu_id.set(self.local_data["stu_id"])
                self.password.set(self.local_data["password"])
                self.start_crawl()
            else:
                showerror(title="自动登录错误", message="config.yml不存在当前目录或格式不正确")

        def get_config(self):
            self.allow_auto_login = os.path.exists('./config.yml')
            if self.allow_auto_login:
                with open("config.yml", "r", encoding="utf-8") as f:
                    try:
                        config_data = yaml.load(f, Loader=yaml.FullLoader)
                        self.local_data = config_data["qiangzhi"]
                    except:
                        self.allow_auto_login = False

        def __init__(self, outer, window):
            # 设置外部类对象
            self.outer = outer
            # 设置窗口
            self.window = window
            # 初始化组件
            # 初始化表单组件和变量
            self.stu_id = tk.StringVar()
            self.password = tk.StringVar()
            self.stu_id_label = tk.Label(window, text="学号", font=('黑体', 15))
            self.password_label = tk.Label(window, text="密码", font=('黑体', 15))
            self.stu_id_input = tk.Entry(window, width=18, borderwidth=0, textvariable=self.stu_id, font=('黑体', 16))
            self.password_input = tk.Entry(window, width=18, borderwidth=0, show='*', textvariable=self.password,
                                           font=('黑体', 16))
            self.form_title_label = tk.Label(window, text="强智系统登录表单", font=('黑体', 24))
            self.start_btn = tk.Button(window, text='开始', bg='#ffffff', borderwidth=0.5, relief='ridge', width=14,
                                       font=('黑体', 15),
                                       command=self.start_crawl, height=1)
            self.cancel_btn = tk.Button(window, text='返回', bg='#ffffff', borderwidth=0.5, relief='ridge', width=14,
                                        font=('黑体', 15),
                                        command=self.back_to_main, height=1)
            self.is_headless = tk.BooleanVar()
            self.is_headless.set(True)
            self.check_is_headless_btn = tk.Checkbutton(self.window, text="爬取时查看详情", variable=self.is_headless,
                                                        onvalue=False, offvalue=True)
            self.get_config()
            self.auto_login_btn = tk.Button(window, text='读取配置文件并开始', bg='#ffffff', borderwidth=0.5, relief='ridge',
                                            width=18,
                                            font=('黑体', 15),
                                            command=self.auto_login, height=1)
            # 初始化爬取界面组件和变量
            # 0是在爬取或未爬取，1是爬取完成，2是有错误
            self.crawling_status = 0
            self.crawl_status_text = tk.StringVar()
            self.crawling_status_base_text = "获取中"
            self.crawl_status_dot_num = 0
            self.crawl_status_label = tk.Label(window, textvariable=self.crawl_status_text, font=('黑体', 24))
            self.crawl_cancel_btn = tk.Button(window, text='返回', bg='#ffffff', borderwidth=0.5, relief='ridge',
                                              width=11,
                                              font=('黑体', 13),
                                              command=self.back, height=2)

    class UnfinishedWorkCrawler:
        def crawl(self) -> None:
            with sync_playwright() as p:
                try:
                    browser = p.chromium.launch(headless=self.is_headless.get(), slow_mo=100)
                    page = browser.new_page()
                    page.goto("http://jshdx.fanya.chaoxing.com/portal")
                    page.click("xpath=/html/body/div[3]/div/div[2]/input")
                    page.fill("#phone", self.phone.get())
                    page.fill("#pwd", self.password.get())
                    page.click("#phoneLoginBtn")
                    page.wait_for_load_state(state='networkidle')
                    if "/space/index" not in page.url:
                        self.crawling_status = 2
                        return
                    courses_frame = page.frame(name="frame_content")
                    page.wait_for_load_state(state='networkidle')
                    courses = courses_frame.locator("#courseList > li > div.course-info > h3 > a")
                    course_hrefs = []
                    for i in range(courses.count()):
                        href = courses.nth(i).get_attribute('href')
                        course_hrefs.append(href)
                    unfinished_works = []
                    for href in course_hrefs:
                        page.goto(href)
                        page.click('"作业"')
                        page.wait_for_load_state(state='networkidle')
                        course_name = page.locator(".textHidden.colorDeep").get_attribute("title")
                        works_frame = page.frame('frame_content-zy')
                        page.wait_for_load_state(state='networkidle')
                        tmp = works_frame.locator("ul > li")
                        for i in range(tmp.count()):
                            if i == 12:
                                break
                            status_text = tmp.nth(i).locator("div.right-content > p.status.fl").inner_text()
                            if status_text == "未交" or status_text == "待互评":
                                work_name = tmp.nth(i).locator("div.right-content > p.overHidden2.fl").inner_text()
                                tmp_rest_time = tmp.nth(i).locator("div.time.notOver")
                                if tmp_rest_time.count() == 0:
                                    rest_time = "已过期"
                                else:
                                    rest_time = tmp_rest_time.inner_text()
                                if rest_time == "已过期" and self.ignore_overdue:
                                    continue
                                unfinished_works.append((course_name, work_name, rest_time))
                    self.unfinished_works = unfinished_works
                    self.crawling_status = 1
                    browser.close()
                except Exception:
                    # traceback.print_exc()
                    self.crawling_status = 3
                    browser.close()

        def crawl_by_requests(self):
            def crypto(origin_pwd):
                context = js2py.EvalJs()
                try:
                    with open("crypto.js") as f:
                        js_content = f.read()
                    context.execute(js_content)
                    result = context.parse(origin_pwd)
                except:
                    return None
                return result

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                }
                data = {
                    "fid": "1907",
                    "uname": self.phone.get(),
                    "password": self.password.get(),
                    "refer": "http%3A%2F%2Fi.mooc.chaoxing.com",
                    "t": True,
                    "validate": "",
                    "doubleFactorLogin": 0,
                    "independentId": 0
                }
                tmp = crypto(data["password"])
                if tmp is None:
                    self.crawling_status = 4
                    return
                data["password"] = tmp
                login_res = requests.post('https://passport2.chaoxing.com/fanyalogin', headers=headers, data=data)
                login_res_json = json.loads(login_res.text)
                if login_res_json["status"] == False:
                    self.crawling_status = 2
                    return
                courses_req_data = {
                    "v": 1665574976002,
                    "rss": 1,
                    "start": 0,
                    "size": 500,
                    "catalogId": 0,
                    "superstarClass": 0,
                    'searchname': ""
                }
                courses_res = requests.post(
                    url='http://mooc2-ans.chaoxing.com/mooc2-ans/visit/courses/list?v=1665574976002&rss=1&start=0&size=500&catalogId=0&superstarClass=0&searchname=',
                    headers=headers,
                    data=courses_req_data,
                    cookies=login_res.cookies.get_dict()
                )
                unfinished_works = []
                soup_1 = BeautifulSoup(courses_res.text, "lxml")
                course_href_tags = soup_1.select(
                    "#courseList > .course.clearfix.catalog_0.learnCourse > div.course-info > h3 > a")
                for tag in course_href_tags:
                    tmp_page_res = requests.get(tag.get("href"), headers=headers,
                                                cookies=login_res.cookies.get_dict())
                    query = parse.parse_qs(parse.urlparse(tag.get("href")).query)
                    soup_2 = BeautifulSoup(tmp_page_res.text, "lxml")
                    course_name = soup_2.select_one("dl.classDl > dd").get("title")
                    enc = soup_2.select_one("#workEnc").get("value")
                    t = soup_2.select_one("#t").get("value")
                    course_query = {
                        "courseId": query["courseid"][0],
                        "classId": query["clazzid"][0],
                        "cpi": query["cpi"][0],
                        "enc": enc,
                        "ut": "s",
                    }
                    work_res = requests.get(
                        "https://mooc1.chaoxing.com/mooc2/work/list?" + parse.urlencode(course_query),
                        cookies=login_res.cookies.get_dict(), headers=headers)
                    soup_3 = BeautifulSoup(work_res.text, "lxml")
                    course_tags = soup_3.select("div.bottomList > ul > li")
                    for tag in course_tags:
                        status_text = tag.select_one("div.right-content > p.status.fl").get_text()
                        if status_text == "未交" or status_text == "待互评":
                            work_name = tag.select_one("div.right-content > p.overHidden2.fl").get_text()
                            try:
                                tmp_rest_time = tag.select_one("div.time.notOver")
                                rest_time = tmp_rest_time.text.replace("\n", "").replace("\r", "").replace(" ", "")
                            except:
                                if self.ignore_overdue.get():
                                    continue
                                rest_time = "已过期"
                            unfinished_works.append((course_name, work_name, rest_time))
                self.unfinished_works = unfinished_works
                self.crawling_status = 1
            except:
                # traceback.print_exc()
                self.crawling_status = 3

        def show_form_element(self):
            self.phone_label.place(x=140, y=159)
            self.phone_input.place(x=215, y=160)
            self.password_label.place(x=160, y=203)
            self.password_input.place(x=215, y=204)
            self.form_title_label.place(x=210, y=95)
            self.start_btn.place(x=105, y=280)
            self.cancel_btn.place(x=365, y=280)
            self.check_is_headless_btn.place(x=10, y=0)
            self.check_ignore_overdue_btn.place(x=10, y=25)
            self.auto_login_btn.place(x=215, y=240)

        def hide_form_element(self):
            self.phone_label.place_forget()
            self.phone_input.place_forget()
            self.password_label.place_forget()
            self.password_input.place_forget()
            self.form_title_label.place_forget()
            self.start_btn.place_forget()
            self.cancel_btn.place_forget()
            self.check_is_headless_btn.place_forget()
            self.check_ignore_overdue_btn.place_forget()
            self.auto_login_btn.place_forget()

        def back_to_main(self):
            self.phone.set("")
            self.password.set("")
            self.hide_form_element()
            self.outer.show_element()

        def show_crawl_element(self):
            self.crawl_status_text.set(self.crawling_status_base_text)
            self.crawl_status_label.pack(expand='yes')
            self.crawl_cancel_btn.place(x=265, y=220)

        def hide_crawl_element(self):
            self.crawl_status_label.pack_forget()
            self.crawl_cancel_btn.place_forget()

        def set_tree_view(self):
            style = ttk.Style()
            style.configure("Treeview.Heading", font=("黑体", 14))
            style.configure("Treeview", font=("宋体", 12), rowheight=20)
            tree = ttk.Treeview(self.window, columns=('course', 'work', 'time'), show="headings",
                                displaycolumns="#all")
            tree.heading('course', text="课程")
            tree.column('course', width=146, anchor=tk.W)
            tree.heading('work', text="作业")
            tree.column('work', width=147, anchor=tk.W)
            tree.heading('time', text="剩余时间")
            tree.column('time', width=146, anchor=tk.W)
            for item in self.unfinished_works:
                tree.insert("", tk.END, values=item)
            self.tree = tree
            tree.pack(side=tk.BOTTOM, fill=tk.X)

        def crawl_monitor(self):
            if self.crawling_status == 0:
                self.crawl_status_dot_num = (self.crawl_status_dot_num + 1) % 4
                self.crawl_status_text.set(self.crawling_status_base_text + "." * self.crawl_status_dot_num)
                timer = Timer(1, self.crawl_monitor, ())
                timer.start()
            elif self.crawling_status == 1:
                self.crawl_status_text.set("获取成功")
                self.crawl_cancel_btn.place_forget()
                self.crawl_cancel_btn.place(x=525, y=10)
                self.set_tree_view()
            elif self.crawling_status == 2:
                self.crawl_status_text.set("登录失败，请重试")
            elif self.crawling_status == 3:
                self.crawl_status_text.set("爬取被意外终止了")
            elif self.crawling_status == 4:
                self.crawl_status_text.set("当前目录不存在crypto.js")

        def start_crawl(self):
            self.hide_form_element()
            self.show_crawl_element()
            self.crawling_status = 0
            self.monitor_timer = Timer(1, self.crawl_monitor, ())
            self.monitor_timer.start()
            if self.is_headless.get():
                self.crawl_timer = Timer(0, self.crawl_by_requests)
            else:
                self.crawl_timer = Timer(0, self.crawl)
            self.crawl_timer.start()

        def back(self):
            self.crawling_status = 3
            if hasattr(self, "crawl_timer") and self.crawl_timer != None:
                self.crawl_timer.cancel()
                self.monitor_timer.cancel()
            if hasattr(self, "tree") and self.tree != None:
                self.tree.pack_forget()
            self.phone.set("")
            self.password.set("")
            self.hide_crawl_element()
            self.show_form_element()

        def auto_login(self):
            self.get_config()
            if self.allow_auto_login:
                self.phone.set(self.local_data["phone"])
                self.password.set(self.local_data["password"])
                self.start_crawl()
            else:
                showerror(title="自动登录错误", message="config.yml不存在当前目录或格式不正确")

        def get_config(self):
            self.allow_auto_login = os.path.exists('./config.yml')
            if self.allow_auto_login:
                with open("config.yml", "r", encoding="utf-8") as f:
                    try:
                        config_data = yaml.load(f, Loader=yaml.FullLoader)
                        self.local_data = config_data["chaoxing"]
                    except:
                        self.allow_auto_login = False

        def __init__(self, outer, window):
            # 设置外部类对象
            self.outer = outer
            # 设置窗口
            self.window = window
            # 初始化组件
            # 初始化表单组件和变量
            self.phone = tk.StringVar()
            self.password = tk.StringVar()
            self.phone_label = tk.Label(window, text="手机号", font=('黑体', 14))
            self.password_label = tk.Label(window, text="密码", font=('黑体', 14))
            self.phone_input = tk.Entry(window, width=18, borderwidth=0, textvariable=self.phone, font=('黑体', 16))
            self.password_input = tk.Entry(window, width=18, borderwidth=0, show='*', textvariable=self.password,
                                           font=('黑体', 16))
            self.form_title_label = tk.Label(window, text="超星登录表单", font=('黑体', 24))
            self.start_btn = tk.Button(window, text='开始', bg='#ffffff', borderwidth=0.5, relief='ridge', width=14,
                                       font=('黑体', 15),
                                       command=self.start_crawl, height=1)
            self.cancel_btn = tk.Button(window, text='返回', bg='#ffffff', borderwidth=0.5, relief='ridge', width=14,
                                        font=('黑体', 15),
                                        command=self.back_to_main, height=1)
            self.is_headless = tk.BooleanVar()
            self.ignore_overdue = tk.BooleanVar()
            self.is_headless.set(True)
            self.ignore_overdue.set(True)
            self.check_is_headless_btn = tk.Checkbutton(self.window, text="模拟浏览器操作", variable=self.is_headless,
                                                        onvalue=False, offvalue=True)
            self.check_ignore_overdue_btn = tk.Checkbutton(self.window, text="忽略过期作业", variable=self.ignore_overdue,
                                                           onvalue=True, offvalue=False)
            self.auto_login_btn = tk.Button(window, text='读取配置文件并开始', bg='#ffffff', borderwidth=0.5, relief='ridge',
                                            width=18,
                                            font=('黑体', 15),
                                            command=self.auto_login, height=1)

            # 初始化爬取界面组件和变量
            # 0是在爬取或未爬取，1是爬取完成，2是登录有误，3是异常,4是文件不存在
            self.crawling_status = 0
            self.crawl_status_text = tk.StringVar()
            self.crawling_status_base_text = "获取中"
            self.crawl_status_dot_num = 0
            self.crawl_status_label = tk.Label(window, textvariable=self.crawl_status_text, font=('黑体', 24))
            self.crawl_cancel_btn = tk.Button(window, text='返回', bg='#ffffff', borderwidth=0.5, relief='ridge',
                                              width=11,
                                              font=('黑体', 13),
                                              command=self.back, height=2)

    def start_crawl_grade_table(self):
        self.hide_element()
        self.grade_table_crawler.show_form_element()

    def start_crawl_unfinished_work(self):
        self.hide_element()
        self.unfinished_work_crawler.show_form_element()

    # 展示组件
    def show_element(self):
        self.crawl_grade_table_btn.place(x=50, y=280)
        self.crawl_unfinished_work_btn.place(x=340, y=280)
        self.title_label.pack(expand="yes")

    # 隐藏组件
    def hide_element(self):
        self.crawl_grade_table_btn.place_forget()
        self.crawl_unfinished_work_btn.place_forget()
        self.title_label.pack_forget()

    def __init__(self, window):
        # 绑定窗口
        self.window = window
        self.window.title('工具')  # 程序的标题名称
        try:
            self.window.iconbitmap('favicon.ico')
        except:
            pass
        # 得到屏幕宽度
        sw = window.winfo_screenwidth()
        # 得到屏幕高度
        sh = window.winfo_screenheight()
        # 窗口宽度
        ww = 640
        # 窗口高度
        wh = 390
        # 窗口宽高为500
        x = (sw - ww) / 2
        y = (sh - wh) / 2
        self.window.geometry("%dx%d+%d+%d" % (ww, wh, x, y))
        self.window.resizable(False, False)  # 固定页面不可放大缩小
        # self.window.iconbitmap("favicon.ico")  # 程序的图标
        # 绑定组件
        self.crawl_grade_table_btn = tk.Button(window, text='获取成绩单', bg='#ffffff', borderwidth=0.5, relief='ridge',
                                               width=20, font=('黑体', 18), command=self.start_crawl_grade_table)
        self.crawl_unfinished_work_btn = tk.Button(window, text='获取待完成作业', bg='#ffffff', borderwidth=0.5,
                                                   relief='ridge',
                                                   width=20, font=('黑体', 18),
                                                   command=self.start_crawl_unfinished_work)
        self.title_label = tk.Label(self.window, text="小工具😅", font=('黑体', 45))
        # 初始化两个类
        self.grade_table_crawler = self.GradeTableCrawler(outer=self, window=window)
        self.unfinished_work_crawler = self.UnfinishedWorkCrawler(outer=self, window=window)
        # 放置组件
        self.show_element()
        window.mainloop()


if __name__ == '__main__':
    w = Window(tk.Tk())
    # 在当前目录下执行 pyinstaller -F -w -i .\favicon.ico main.py
