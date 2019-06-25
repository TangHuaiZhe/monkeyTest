# -*- coding: utf-8 -*-import os
import os
import platform
import time


class AndroidDebugBridge(object):
    @staticmethod
    def call_adb(command):
        command_result = ''
        command_text = f'adb {command}'
        print("执行命令：" + command_text)
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line:
                break
            command_result += line
        results.close()
        return command_result

    # 检查设备
    def attached_devices(self):
        result = self.call_adb("devices")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]

    # 重启
    def reboot(self, option):
        command = "reboot"
        if len(option) > 7 and option in ("bootloader", "recovery",):
            command = f"{command} {option.strip()}"
        self.call_adb(command)

    # 将电脑文件拷贝到手机里面
    def push(self, local, remote):
        result = self.call_adb(f"push {local} {remote}")
        return result

    # 拉数据到本地
    def pull(self, remote, local):
        result = self.call_adb(f"pull {remote} {local}")
        return result

    # 打开指定app
    def open_app(self, packageName, activity, devices):
        result = self.call_adb(
            f"-s {devices} shell am start -n {packageName}/{activity}")
        check = result.partition('\n')[2].replace('\n', '').split('\t ')
        if check[0].find("Error") >= 1:
            return False
        else:
            return True

    # 根据包名得到进程id
    def get_app_pid(self, pkg_name):
        string = self.call_adb(f"shell ps | grep {pkg_name}")
        if string == '':
            return "the process doesn't exist."
        result = string.split(" ")
        return result[4]

    def isOnTop(self, pkg_name, moduleKey):
        """
        判断测试的app的module是否在top
        :param pkg_name:测试app包名
        :param moduleKey:app模块中关键词 todo 支持多个模块
        :return:
        """
        result = self.getCurrentAty()
        if result == '':
            return "the process doesn't exist."
        print(result)
        if pkg_name in result and moduleKey in result and "leakcanary" not in result:
            return True
        else:
            return False

    def getCurrentAty(self):
        if platform.system() == "Windows":
            result = self.call_adb("shell dumpsys activity | findstr mResumedActivity")
        else:
            result = self.call_adb("shell dumpsys activity | grep mResumedActivity")
        return result

    def isStopHow(self, startTime, currentActivity, seconds):
        """
        判断测试app是否在某个页面停留过久，防止测试卡死
        :param startTime:开始计算的时间
        :param currentActivity:当前前台的aty
        :param seconds: 停留时间
        :return:是否
        """
        while currentActivity == self.getCurrentAty():
            end = time.time()
            print(f"同一页面持续测试时间: {(end - startTime)}")
            if end - startTime > seconds:
                print("超过阈值：即将随机打开activity")
                return True
            else:
                return False
        else:
            return False
