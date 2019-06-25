# -*- coding: utf-8 -*-
import datetime
import os
import random
import time
import platform
from multiprocessing import Pool
from typing import Dict, Union
from internal import AdbCommon
from internal import Config
from internal.AdbCommon import AndroidDebugBridge

adb = AdbCommon.AndroidDebugBridge()
monkeyConfig = Config.MonkeyConfig()


def runnerPool():
    devices_Pool = []
    devices = adb.attached_devices()
    if devices:
        for item in range(0, len(devices)):
            _app: Dict[str, Union[str, int]] = {"devices": devices[item], "num": len(devices)}
            devices_Pool.append(_app)
        pool = Pool(len(devices))
        pool.map(start, devices_Pool)
        pool.close()
        pool.join()
    else:
        print("设备不存在?")


def start(devices):
    device = devices["devices"]
    deviceNum = devices["num"]
    print(f"start device {device};num {deviceNum}")

    # monkeyConfig = BaseMonkeyConfig.monkeyConfig()
    # 打开想要的activity
    adb.open_app(monkeyConfig.package_name, monkeyConfig.activity[0], device)

    # log目录
    logDir = os.path.join("log", f"{datetime.datetime.now().strftime('%Y%m%d_%p_%H%M%S')}")
    os.makedirs(logDir)

    # adb log
    adbLogFileName = os.path.join(logDir, "logcat.log")

    # monkey Log
    monkeyLogFile = os.path.join(logDir, "monkey.log")
    monkeyConfig.monkeyCmd = f"adb -s {device} shell {monkeyConfig.monkeyCmd + monkeyLogFile}"

    # 开始测试
    start_monkey(monkeyConfig.monkeyCmd, logDir)

    start_activity_time = time.time()
    while True:
        # 判断测试的app的module是否在top
        if AndroidDebugBridge().isOnTop(monkeyConfig.package_name,
                                        monkeyConfig.module_key) is False:
            # 如果卡死 随机打开一个配置aty
            adb.open_app(monkeyConfig.package_name, monkeyConfig.activity[0],
                         device)
        currentActivity = AndroidDebugBridge().getCurrentAty()
        time.sleep(2)

        # 判断测试app是否在某个页面停留过久，防止测试卡死
        if AndroidDebugBridge().isStopHow(start_activity_time, currentActivity, 10):
            adb.open_app(monkeyConfig.package_name,
                         random.choice(monkeyConfig.activity), device)
            start_activity_time = time.time()

        with open(monkeyLogFile, "r", encoding='utf-8') as monkeyLog:
            if monkeyLog.read().count('Monkey finished') > 0:
                print(f"{device}\n测试完成咯")
                break

    with open(adbLogFileName, "r", encoding='utf-8') as logfile:
        print(
            f"{device}\n存在{logfile.read().count('FATAL EXCEPTION')}个Crash!!!!"
            f"查看{adbLogFileName}文件")


# 开始脚本测试
def start_monkey(monkeyCmd, logDir):
    """
    :param monkeyCmd:monkey测试的命令
    :param logDir:本次测试的log目录
    """

    os.popen(monkeyCmd)
    print(f"start_monkey {monkeyCmd}")

    # Monkey时手机日志,logcat
    logFileName = os.path.join(logDir, "logcat.log")
    cmd2 = f"adb logcat -d >{logFileName}"
    os.popen(cmd2)

    # "导出traces文件 用于分析ANR"
    traceFilename = os.path.join(logDir, "anr_traces.log")
    cmd3 = f"adb shell cat /data/anr/traces.txt>{traceFilename}"
    os.popen(cmd3)


def killPort():
    os.popen("adb kill-server")
    os.popen("adb start-server")
    os.popen("adb root")


if __name__ == '__main__':
    print(f"当前操作系统 {platform.system()}")
    killPort()
    time.sleep(1)
    runnerPool()
