# -*- coding: utf-8 -*-


class MonkeyConfig(object):
    # 测试的app包名
    package_name = "com.sdpopen.demo"

    # 测试app中模块的关键词
    module_key = "com.sdpopen.wallet"

    # todo 自动找到apk中exported的activity
    # 卡死状态随机跳转的activity,第一个元素为测试初始页
    activity = ["com.sdpopen.wallet.home.activity.HomeActivity",
                "com.sdpopen.wallet.bankmanager.activity.BankCardManagerActivity",
                "com.sdpopen.wallet.charge_transfer_withdraw.activity.DepositActivity",
                "com.sdpopen.wallet.bankmanager.activity.BindCardActivity",
                "com.sdpopen.wallet.charge_transfer_withdraw.activity.TransferActivity",
                "com.sdpopen.wallet.home.activity.RemainActivity",
                "com.sdpopen.wallet.charge_transfer_withdraw.activity.WithdrawActivity"]

    monkeyCmd = f"monkey -p {package_name} --throttle 300  " \
                "--pct-appswitch 5 --pct-touch 30 --pct-motion 60 --pct-anyevent 5  " \
                "--ignore-timeouts --ignore-crashes   --monitor-native-crashes -v -v -v 3000 > "
