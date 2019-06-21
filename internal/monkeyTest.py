# -*- coding: utf-8 -*-
import datetime
import os
import random
import time
from multiprocessing import Pool
from typing import Dict, Union
o
from internal import AdbCommon, BaseMonkeyConfig
from internal.AdbCommon import AndroidDebugBridge

adb = AdbCommon.AndroidDebugBridge()

# todo 自动找到apk中exported的activity
# 卡死状态随机跳转的activity,第一个元素为测试初始页
activity = ["com.sdpopen.wallet.home.activity.HomeActivity",
            "com.sdpopen.wallet.bankmanager.activity.BankCardManagerActivity",
            "com.sdpopen.wallet.charge_transfer_withdraw.activity.DepositActivity",
            "com.sdpopen.wallet.bankmanager.activity.BindCardActivity",
            "com.sdpopen.wallet.charge_transfer_withdraw.activity.TransferActivity",
            "com.sdpopen.wallet.home.activity.RemainActivity",
            "com.sdpopen.wallet.charge_transfer_withdraw.activity.WithdrawActivity"]


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

    monkeyConfig = BaseMonkeyConfig.monkeyConfig()
    # 打开想要的activity
    adb.open_app(monkeyConfig["package_name"], activity[0], device)

    # log目录
    monkeyConfig["log"] = os.path.join("log",
                                       f"{datetime.datetime.now().strftime('%Y%m%d_%p_%H%M%S')}")
    os.makedirs(monkeyConfig["log"])

    monkeyConfig["monkey_log"] = os.path.join(monkeyConfig["log"], "monkey.log")
    monkeyConfig["cmd"] = monkeyConfig['cmd'] + monkeyConfig["monkey_log"]

    start_monkey("adb -s " + device + " shell " + monkeyConfig["cmd"], monkeyConfig["log"])
    start_activity = time.time()
    while True:
        if AndroidDebugBridge().isOnTop(monkeyConfig["package_name"],
                                        monkeyConfig["key"]) is False:
            adb.open_app(monkeyConfig["package_name"], activity[0],
                         device)
        currentActivity = AndroidDebugBridge().call_adb(
            "shell dumpsys activity | grep mResumedActivity")
        time.sleep(2)
        if AndroidDebugBridge().isStopHow(start_activity, currentActivity, 10):
            adb.open_app(monkeyConfig["package_name"],
                         random.choice(activity), device)
            start_activity = time.time()

        with open(monkeyConfig["monkey_log"], "r", encoding='utf-8') as monkeyLog:
            if monkeyLog.read().count('Monkey finished') > 0:
                print(str(device) + "\n测试完成咯")
                break
    logFileName = os.path.join(monkeyConfig["log"], "logcat.log")
    with open(logFileName, "r", encoding='utf-8') as logfile:
        if logfile.read().count('beginning of crash') > 0:
            print(str(device) + "\n存在Crash!! 查看log/logcat文件")


# 开始脚本测试
def start_monkey(cmd, logDir):
    # Monkey测试结果日志:monkey_log
    os.popen(cmd)
    print(cmd)

    # Monkey时手机日志,logcat
    logFileName = os.path.join(logDir, "logcat.log")
    cmd2 = "adb logcat -d >%s" % logFileName
    os.popen(cmd2)

    # "导出traces文件"
    traceFilename = os.path.join(logDir, "anr_traces.log")
    cmd3 = "adb shell cat /data/anr/traces.txt>%s" % traceFilename
    os.popen(cmd3)


def killport():
    os.popen("adb kill-server")
    os.popen("adb start-server")
    os.popen("adb root")


if __name__ == '__main__':
    killport()
    time.sleep(1)
    runnerPool()

# back:adb shell input keyevent 4
