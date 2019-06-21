# monkeyTest
环境:Python3.4以上

配置文件:Config.py

`package_name`:测试的app包名

`module_key`:测试app的模块

`activity`:卡死状态随机跳转的activity列表,第一个元素为测试初始页

`monkeyCmd`:monkey测试的具体命令,设置触摸百分比，点击次数此处修改

Todo:

通过apk安装包自动找到adb可以跳转的Activity,写入配置

支持多个`module_key`

