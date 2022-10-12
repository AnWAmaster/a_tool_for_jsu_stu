本软件是个人的`Playwright`和`requests`和`tkinter`的小作品
可以供吉首大学学生来获取个人成绩表以及获取未完成作业信息

文件介绍：

1. main.py 是主要软件，供用户使用
2. crypto.js(必需),项目逻辑所需
3. config.yml(不必需),一键登录功能所需
4. favicon.ico(不必需),存在时可改变程序左上角标志

打包方式：

	1. 安装pyinstaller
	2. 在当前目录执行 `pyinstaller -F -w -i .\favicon.ico main.py`
	3. 打包后文件处于./dist/文件夹下

作者邮箱：2213732736@qq.com