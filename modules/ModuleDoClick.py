# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from os.path import abspath, dirname
from time import sleep
import random
import win32com.client
from win32gui import SetForegroundWindow, GetWindowRect
from win32api import MAKELONG, SendMessage
from win32con import WM_LBUTTONUP, WM_LBUTTONDOWN, WM_ACTIVATE, WA_ACTIVE
from pyautogui import position, click, moveTo

from modules.ModuleClickModSet import ClickModSet
from modules.ModuleHandleSet import HandleSet
from modules.ModuleGetConfig import ReadConfigFile


class DoClick:
    def __init__(self, pos, click_mod, handle_num=0):
        super(DoClick, self).__init__()
        self.click_mod = click_mod
        self.handle_num = handle_num
        self.pos = pos
        rc = ReadConfigFile()
        other_setting = rc.read_config_other_setting()
        self.ex_click_probability = float(other_setting[10])  # 从配置文件读取是否有设置额外偏移点击概率

    def windows_click(self):
        """
        点击目标位置,可后台点击（仅兼容部分窗体程序）
        """
        if self.pos is not None:
            pos = self.pos
            handle_num = self.handle_num
            px, py = ClickModSet.choice_mod_pos(self.click_mod)
            cx = int(px + pos[0])
            cy = int(py + pos[1]) - 40  # 减去40是因为window这个框占用40单位的高度

            # 模拟鼠标指针 点击指定位置
            long_position = MAKELONG(cx, cy)
            SendMessage(handle_num, WM_ACTIVATE, WA_ACTIVE, 0)
            SendMessage(handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
            sleep((random.randint(8, 35)) / 100)  # 点击弹起改为随机
            SendMessage(handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起
            print(f"<br>点击坐标: [ {cx} , {cy} ] <br>窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

            # 以下代码模拟真实点击，怀疑痒痒鼠会记录点击坐标数据，然后AI判断是否规律（比如一段时间内，每次都总点某个按钮附近，不超过100像素，就有风险），
            # 如果只是随机延迟+坐标偏移，可能骗不过后台
            # 这里模拟正常点击偶尔会多点一次的情况，另外再增加混淆点击，使整体点击看起来不那么规律
            if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
                roll_num = random.randint(0, 99)  # roll 0-99，触发几率在配置文件可设置
                if roll_num > (1 - self.ex_click_probability / 2) * 100:  # 匹配坐标附近的，不偏移太远(一半的概率分给附近)
                    sleep((random.randint(10, 35)) / 100)  # 随机延迟0.1-0.35秒
                    SendMessage(handle_num, WM_LBUTTONDOWN, 0, MAKELONG(cx, cy))  # 模拟鼠标按下
                    sleep((random.randint(4, 35)) / 100)  # 点击弹起随机延迟
                    SendMessage(handle_num, WM_LBUTTONUP, 0, MAKELONG(cx, cy))  # 模拟鼠标弹起
                    print(f"<br>点击偏移坐标: [ {cx}, {cy} ]")
                elif roll_num < self.ex_click_probability * 50:  # 随机点击其他地方(另一半的概率分给其他地方)
                    sleep((random.randint(10, 35)) / 100)  # 随机延迟0.1-0.35秒
                    handle_set = HandleSet('', handle_num)

                    # 点击屏幕中心，偏右下的位置
                    mx = int((handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]) / 1.68 + px)
                    my = int((handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]) / 1.68 + py)
                    SendMessage(handle_num, WM_LBUTTONDOWN, 0, MAKELONG(mx, my))  # 模拟鼠标按下
                    sleep((random.randint(4, 35)) / 100)  # 点击弹起随机延迟
                    SendMessage(handle_num, WM_LBUTTONUP, 0, MAKELONG(mx, my))  # 模拟鼠标弹起
                    print(f"<br>点击偏移坐标: [ {mx}, {my} ]")

            return True, [cx, cy]

    def adb_click(self, device_id):
        """数据线连手机点击"""
        if self.pos is not None:
            pos = self.pos
            px, py = ClickModSet.choice_mod_pos(self.click_mod)
            cx = int(px + pos[0])
            cy = int(py + pos[1])

            # 使用modules下的adb工具执行adb命令
            command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {cx} {cy}'
            HandleSet.deal_cmd(command)
            # system(command)
            print(f"<br>点击设备 [ {device_id} ] 坐标: [ {cx} , {cy} ]")

            # 模拟真实点击、混淆点击热区
            if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
                roll_num = random.randint(0, 99)  # roll 0-99，触发几率在配置文件可设置
                if roll_num > (1 - self.ex_click_probability / 2) * 100:  # 匹配坐标附近的，不偏移太远(一半的概率分给附近)
                    sleep((random.randint(10, 35)) / 100)  # 随机延迟0.1-0.35秒
                    command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {cx} {cy}'
                    HandleSet.deal_cmd(command)
                    print(f"<br>点击设备 [ {device_id} ] 额外偏移坐标: [ {cx} , {cy} ]")
                elif roll_num < self.ex_click_probability * 50:  # 随机点击其他地方(另一半的概率分给其他地方)
                    sleep((random.randint(10, 35)) / 100)  # 随机延迟0.1-0.35秒
                    mx = random.randint(50, 1050) + px
                    my = random.randint(50, 1050) + py
                    command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {mx} {my}'
                    HandleSet.deal_cmd(command)
                    print(f"<br>点击设备 [ {device_id} ] 额外偏移坐标: [ {mx} , {my} ]")

            return True, [cx, cy]

    def windows_click_bk(self):
        """
        点击目标位置,只能前台点击（兼容所有窗体程序）
        """
        # 前台点击，窗口必须置顶，兼容所有窗口（模拟器、云游戏等）点击
        pos = self.pos
        handle_num = self.handle_num
        px, py = ClickModSet.choice_mod_pos(self.click_mod)
        x1, y1, x2, y2 = GetWindowRect(handle_num)

        # 设置随机偏移范围，避免封号
        cx = int(px + pos[0])
        cy = int(py + pos[1]) - 40  # 减去40是因为window这个框占用40单位的高度

        # 计算绝对坐标位置
        jx = cx + x1
        jy = cy + y1

        # 把窗口置顶，并进行点击
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        SetForegroundWindow(handle_num)
        sleep(0.2)  # 置顶后等0.2秒再点击
        now_pos = position()
        moveTo(jx, jy)  # 鼠标移至目标
        click(jx, jy)
        print(f"<br>点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

        # 模拟真实点击、混淆点击热区
        if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
            roll_num = random.randint(0, 99)  # roll 0-99，触发几率在配置文件可设置
            if roll_num > (1 - self.ex_click_probability / 2) * 100:  # 匹配坐标附近的，不偏移太远(一半的概率分给附近)
                sleep((random.randint(10, 35)) / 100)  # 随机延迟0.1-0.35秒
                click(jx, jy)
                print(f"<br>点击偏移坐标: [ {jx}, {jy} ]")
            elif roll_num < self.ex_click_probability * 50:  # 随机点击其他地方(另一半的概率分给其他地方)
                sleep((random.randint(10, 35)) / 100)  # 随机延迟0.1-0.35秒
                mx = int(x1 + (x2 - x1) / 1.68 + px)
                my = int(x1 + (x2 - x1) / 1.68 + py)
                click(mx, my)
                print(f"<br>点击偏移坐标: [ {mx}, {my} ]")
        moveTo(now_pos[0], now_pos[1])

        return True, [cx, cy]
