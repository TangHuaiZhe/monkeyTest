# python module for interacting with adb
import os
import time


class AndroidDebugBridge(object):
    @staticmethod
    def call_adb(command):
        command_result = ''
        command_text = 'adb %s' % command
        print("执行命令：" + command_text)
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line:
                break
            command_result += line
        results.close()
        return command_result

    # check for any fastboot device
    def fastboot(self, device_id):
        pass

    # 检查设备
    def attached_devices(self):
        result = self.call_adb("devices")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]

    # 状态
    def get_state(self):
        result = self.call_adb("get-state")
        result = result.strip(' \t\n\r')
        return result or None

    # 重启
    def reboot(self, option):
        command = "reboot"
        if len(option) > 7 and option in ("bootloader", "recovery",):
            command = "%s %s" % (command, option.strip())
        self.call_adb(command)

    # 将电脑文件拷贝到手机里面
    def push(self, local, remote):
        result = self.call_adb("push %s %s" % (local, remote))
        return result

    # 拉数据到本地
    def pull(self, remote, local):
        result = self.call_adb("pull %s %s" % (remote, local))
        return result

    # 同步更新 很少用此命名
    def sync(self, directory, **kwargs):
        command = "sync %s" % directory
        if 'list' in kwargs:
            command += " -l"
            result = self.call_adb(command)
            return result

    # 打开指定app
    def open_app(self, packagename, activity, devices):
        result = self.call_adb(
            "-s " + devices + " shell am start -n %s/%s" % (packagename, activity))
        check = result.partition('\n')[2].replace('\n', '').split('\t ')
        if check[0].find("Error") >= 1:
            return False
        else:
            return True

    # 根据包名得到进程id
    def get_app_pid(self, pkg_name):
        string = self.call_adb("shell ps | grep " + pkg_name)
        if string == '':
            return "the process doesn't exist."
        result = string.split(" ")
        return result[4]

    # 判断测试的app的key是否在top
    def isOnTop(self, pkg_name, key):
        result = self.call_adb("shell dumpsys activity | grep mResumedActivity")
        if result == '':
            return "the process doesn't exist."
        print(result)
        if result.__contains__(pkg_name) and result.__contains__(
                key) and (
                result.__contains__("leakcanary") is False) and (
                result.__contains__("com.alvin.wallet.ui.MainActivity") is False):
            return True
        else:
            return False

    # 判断测试app是否在某个页面停留过久，防止测试卡死
    def isStopHow(self, startTime, currentActivity, seconds):
        while currentActivity == self.call_adb("shell dumpsys activity | grep mResumedActivity"):
            end = time.time()
            print("同一页面持续测试时间:" + str(end - startTime))
            if end - startTime > seconds:
                print("超过阈值：随机打开activity")
                return True
            else:
                return False
        else:
            return False
