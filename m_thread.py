import threading
import datetime
import random
import pub
import sys
import os
import time
import paho.mqtt.client as mqtt
from web3 import Web3, HTTPProvider
w3 = Web3(HTTPProvider('http://localhost:8545'))
from eth_account.messages import encode_defunct
import json


REPORT_TOPIC1 = 'register'  # 设备订阅注册主题
REPORT_TOPIC2 = 'verify'  # 认证主题
REPORT_TOPIC3 = 'state'  # 认证主题
exitFlag = 0
num = 0
count = 0
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")


def inverse(a):
    b = ''
    c = ''
    i = 1
    while a[i] != ',':
        b = b + a[i]
        i = i + 1

    i = i + 2

    while a[i] != ')':
        c = c + a[i]
        i = i + 1

    tup = (int(b), int(c))
    return tup


class ac_thread(threading.Thread):
    def __init__(self, threadID, name, delay, st, et, mod, state, cmd, deviceid, sk):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.st = st
        self.et = et
        self.kw = random.randint(700, 1000)
        self.mod = mod
        self.state = state
        self.cmd = " "
        self.public_key = -1
        self.secret_key = sk
        self.d_certification = -1
        self.deviceid = deviceid
        self.filename = name + '.txt'
        with open(self.filename, 'w') as self.f:
            self.f.write('')

    def reg(self):
        client = mqtt.Client(self.deviceid, transport='tcp')
        T1 = time.time()

        def on_connect(client, userdata, flags, rc):
            client.subscribe(REPORT_TOPIC1)  # 注册主题
            client.subscribe(REPORT_TOPIC2)
            client.subscribe(REPORT_TOPIC3)

        def on_message(client, userdata, msg):
            """
            接收客户端发送的消息
            :param client: 连接信息
            :param userdata:
            :param msg: 客户端返回的消息
            :return:
            """
            # print("Start server!")
            payload = json.loads(msg.payload.decode('utf-8'))
            with open(self.filename, 'a') as self.f:
                if self.deviceid in str(payload) or str(self.public_key) in str(payload) or str(self.d_certification) in str(payload):
                    # print(payload)
                    # self.f.write(str(payload) + '\n')
                    if "confirm_register" in str(payload):
                        self.f.write(str(payload) + '\n')
                        print(self.name + "  服务器注册通过")
                        #设备生成公钥私钥
                        ####换一种方式获取公钥私钥
                        # self.secret_key, self.public_key = ECDSA.make_keypair()
                        # self.secret_key = "503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb"
                        w3.eth.account.privateKeyToAccount(self.secret_key)
                        #########################################################
                        ##改这里的参数
                        self.public_key = w3.eth.accounts[9 + self.threadID]
                        # print(self.public_key)
                        self.f.write("当前设备的公钥为： " + str(self.public_key) + '\n' + "私钥为： " + str(self.secret_key) + '\n')
                        pub.clicent_main(str(self.public_key), self.deviceid, "verify_start")
                    elif 'reject' in str(payload):
                        self.f.write(str(payload) + '\n')
                        print(self.name + "服务器拒绝注册, 因为使用了未经过授权的设备序列号")
                        server_stop(client)
                    elif payload['cmd'] == "verify":
                        self.f.write(str(payload) + '\n')
                        print(self.name + "  开始进行身份验证")
                        #######签名过程#######
                        ##使用web3.py 的生成算法
                        if self.threadID == 4:
                            ##如果设备将认证的消息进行更改，发现没有问题，是否需要发送来的信息与验证信息一致？
                            raw_msg = payload['msg'] + "syx"
                        else:
                            raw_msg = payload['msg']
                        eip_191_msg = encode_defunct(text=raw_msg)
                        if self.threadID == 4:
                            signed_message = w3.eth.account.sign_message(eip_191_msg, private_key="503f3812c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb")
                        else:
                            signed_message = w3.eth.account.sign_message(eip_191_msg, private_key=self.secret_key)
                        msg_hash = w3.toHex(signed_message.messageHash)
                        msg_sig = w3.toHex(signed_message.signature)
                        ####第一个是加密信息，第二个是数字签名
                        sig = []
                        sig.append(msg_hash)
                        sig.append(msg_sig)
                        pub.clicent_main(str(sig), str(self.public_key), "shake")
                    elif payload['cmd'] == 'shake_result':
                        self.f.write(str(payload) + '\n')
                        if 'signature matches' in str(payload):
                            print(self.name + " 设备已通过明文认证！")
                        else:
                            print(self.name + " 设备未通过明文认证！")
                    elif payload['cmd'] == 'certification':
                        self.f.write(str(payload) + '\n')
                        a = payload['msg']
                        self.d_certification = a
                        self.f.write("设备的Token： " + a + '\n')
                        pub.clicent_main(self.name + "已成功注册 ", str(self.public_key), 'deregister')
                        acc = input("设备:" + self.name + "已经成功注册，是否需要发起接入？\n")
                        if acc == "1":
                            pub.clicent_main(self.name + "access require ", str(self.public_key), 'access_require')
                        else:
                            print("设备: " + self.name + "进入休眠状态....")
                            time.sleep(10000000)
                            acc = input("设备已经成功注册，是否需要发起接入？")
                    elif payload['cmd'] == 'access_confirm':        #有问题
                        self.f.write(str(payload) + '\n')
                        pub.clicent_main(str(self.d_certification), str(self.public_key), 'access_shake')
                    elif payload['cmd'] == 'certification_match':
                        self.f.write(str(payload) + '\n')
                        pub.clicent_main("设备：" + self.name + "已成功接入", str(self.public_key), "state")
                        print("设备：" + self.name + "已成功接入")
                        self.keep_alive()
                        self.f.write("设备：" + self.name + "已成功接入" + '\n')
                    elif payload['cmd'] == 'invalid_certification':
                        print("设备：" + self.name + "接入失败")

        def sever_connect(client):
            client.on_connect = on_connect  # 启用订阅模式
            client.on_message = on_message  # 接收消息
            client.connect("127.0.0.1", 1883, 60)  # 链接
            # client.loop_start()  # 以start方式运行，需要启动一个守护线程，让服务端运行，否则会随主线程死亡
            client.loop_forever()  # 以forever方式阻塞运行。

        def server_stop(client):
            client.loop_stop()  # 停止服务端
            sys.exit(0)

        sever_connect(client)

    def change(self, cmd, value):
        if cmd == "st":
            self.st = value
        elif cmd == "mod":
            self.mod = value
        elif cmd == "name":
            self.name = value
        elif cmd == "mod":
            self.mod = value
        elif cmd == "state":
            self.state = value

        else: return False

    def keep_alive(self):
        while True:
            with open(self.filename, 'a') as self.f:
                if int(self.st) - int(self.et) >= 20:
                    self.kw = random.randint(900, 1000)
                elif int(self.st) - int(self.et) >= 10:
                    self.kw = random.randint(800, 900)
                else: self.kw = random.randint(700, 800)

                if int(self.et) < int(self.st):
                    self.et = self.et + random.randint(1, 2)
                else:
                    self.et = self.et - random.randint(1, 2)
                self.f.write("当前的室温为： " + str(self.et) + " 设定温度为：" + str(self.st) + " 模式：" + self.mod + " 功耗情况： " + str(self.kw) + '\n')
            time.sleep(self.delay)

    def run(self):
        pub.clicent_main(" ", self.deviceid, "deregister")
        global count, num
        self.reg()

        while True:
            if self.state == "0":
                pub.clicent_main(self.name + "运行结束！", self.deviceid, "state")
                return True
            time.sleep(self.delay)
            count = count + 1


class mon_thread(threading.Thread):
    def __init__(self, threadID, name, delay, state, cmd, deviceid, sk):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.current_time = datetime.date.today()
        self.current = time.strftime("%H:%M:%S")
        self.state = state
        self.cmd = " "
        self.public_key = -1
        self.secret_key = sk
        self.d_certification = -1
        self.deviceid = deviceid
        self.filename = name + '.txt'
        with open(self.filename, 'w') as self.f:
            self.f.write('')

    def reg(self):
        client = mqtt.Client(self.deviceid, transport='tcp')

        def on_connect(client, userdata, flags, rc):
            client.subscribe(REPORT_TOPIC1)  # 注册主题
            client.subscribe(REPORT_TOPIC2)
            client.subscribe(REPORT_TOPIC3)

        def on_message(client, userdata, msg):
            """
            接收客户端发送的消息
            :param client: 连接信息
            :param userdata:
            :param msg: 客户端返回的消息
            :return:
            """
            # print("Start server!")
            payload = json.loads(msg.payload.decode('utf-8'))
            with open(self.filename, 'a') as self.f:
                if self.deviceid in str(payload) or str(self.public_key) in str(payload) or str(self.d_certification) in str(payload):
                    # print(payload)
                    # self.f.write(str(payload) + '\n')
                    if "confirm_register" in str(payload):
                        self.f.write(str(payload) + '\n')
                        print(self.name + "  服务器注册通过")
                        #设备生成公钥私钥
                        ####换一种方式获取公钥私钥
                        # self.secret_key, self.public_key = ECDSA.make_keypair()
                        # self.secret_key = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
                        w3.eth.account.privateKeyToAccount(self.secret_key)
                        #########################################################
                        ##改这里的参数
                        self.public_key = w3.eth.accounts[9 + self.threadID]
                        # print(self.public_key)
                        self.f.write("当前设备的公钥为： " + str(self.public_key) + '\n' + "私钥为： " + str(self.secret_key) + '\n')
                        pub.clicent_main(str(self.public_key), self.deviceid, "verify_start")
                    elif 'reject' in str(payload):
                        self.f.write(str(payload) + '\n')
                        print(self.name + "服务器拒绝注册")
                        server_stop(client)
                    elif payload['cmd'] == "verify":
                        self.f.write(str(payload) + '\n')
                        print(self.name + "  开始进行身份验证")
                        #######签名过程#######
                        ##使用web3.py 的生成算法
                        raw_msg = payload['msg']
                        eip_191_msg = encode_defunct(text=raw_msg)
                        signed_message = w3.eth.account.sign_message(eip_191_msg, private_key=self.secret_key)
                        msg_hash = w3.toHex(signed_message.messageHash)
                        msg_sig = w3.toHex(signed_message.signature)
                        ####第一个是加密信息，第二个是数字签名
                        sig = []
                        sig.append(msg_hash)
                        sig.append(msg_sig)
                        pub.clicent_main(str(sig), str(self.public_key), "shake")
                    elif payload['cmd'] == 'shake_result':
                        self.f.write(str(payload) + '\n')
                        if 'signature matches' in str(payload):
                            print(self.name + " 设备已通过明文认证！")
                        else:
                            print(self.name + " 设备未通过明文认证！")
                    elif payload['cmd'] == 'certification':
                        self.f.write(str(payload) + '\n')
                        a = payload['msg']
                        self.d_certification = a
                        self.f.write("设备的Token： " + a + '\n')
                        pub.clicent_main(self.name + "已成功注册 ", str(self.public_key), 'deregister')
                        acc = input("设备:" + self.name + "已经成功注册，是否需要发起接入？\n")
                        if acc == "1":
                            pub.clicent_main(self.name + "access require ", str(self.public_key), 'access_require')
                        else:
                            print("设备: " + self.name + "进入休眠状态....")
                            time.sleep(10000000)
                            acc = input("设备已经成功注册，是否需要发起接入？")
                    elif payload['cmd'] == 'access_confirm':        #有问题
                        self.f.write(str(payload) + '\n')
                        if self.threadID == 5:
                            self.d_certification = "0x61c8d6cbebc2e1678857522ee893b599651a2fbd48eadcfef62b282b1ef5f9c2574508c43a0e44d976f24adc49884e1988fb5e8d7584733b4833be43027c0ed01b"
                        pub.clicent_main(str(self.d_certification), str(self.public_key), 'access_shake')
                    elif payload['cmd'] == 'certification_match':
                        self.f.write(str(payload) + '\n')
                        pub.clicent_main("设备：" + self.name + "已成功接入", str(self.public_key), "state")
                        print("设备：" + self.name + "已成功接入")
                        self.f.write("设备：" + self.name + "已成功接入" + '\n')
                        self.keep_alive()
                    elif payload['cmd'] == 'invalid_certification':
                        print("设备：" + self.name + "接入失败")



        def sever_connect(client):
            client.on_connect = on_connect  # 启用订阅模式
            client.on_message = on_message  # 接收消息
            client.connect("127.0.0.1", 1883, 60)  # 链接
            # client.loop_start()  # 以start方式运行，需要启动一个守护线程，让服务端运行，否则会随主线程死亡
            client.loop_forever()  # 以forever方式阻塞运行。

        def server_stop(client):
            client.loop_stop()  # 停止服务端
            sys.exit(0)

        sever_connect(client)


    def change(self, cmd, value):
        if cmd == "st":
            self.st = value
        elif cmd == "mod":
            self.mod = value
        elif cmd == "name":
            self.name = value
        elif cmd == "mod":
            self.mod = value
        elif cmd == "state":
            self.state = value

        else: return False

    def run(self):
        pub.clicent_main(" ", self.deviceid, "deregister")
        global count, num
        self.reg()

    def keep_alive(self):
        # print("公钥为：" + str(self.public_key) + "私钥：" + str(self.secret_key))
        while True:
            self.current_time = datetime.date.today()
            self.current = time.strftime("%H:%M:%S")
            self.f.write("这是" + self.name + "线程,当前的日期为:" + str(self.current_time) + "当前时间：" + self.current + "当前状态：" + self.state + '\n')
            time.sleep(self.delay)


class cleaner_thread(threading.Thread):
    def __init__(self, threadID, name, delay, e_humidity, s_humidity, state, cmd):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
        self.s_humidity = s_humidity
        self.state = state
        self.cmd = " "
        self.e_humidity = e_humidity
        self.public_key = 0
        self.secret_key = 0
        self.d_certification = 0

    # def get_in(self):
    #     psw = input("输入管理员密码：")
    #     if CA.verify_device(psw) == True:
    #         self.secret_key, self.public_key = CA.deliver_key()
    #         self.d_certification = CA.digital_certification(self.public_key)
    #     else:
    #         return False

    def change(self, cmd, value):
        if cmd == "state":
            self.state = value
        elif cmd == "name":
            self.name = value
        elif cmd == "s_humidity":
            self.s_humidity = value

    def keep_alive(self, T1, T2):
        if int(T2 - T1) % 5 == 0:
            if int(self.e_humidity) < int(self.s_humidity):
                self.e_humidity = self.e_humidity + random.randint(1, 2)
            else:
                self.e_humidity = self.e_humidity - random.randint(1, 2)

    def run(self):
        T1 = time.time()
        while True:
            if self.state == "0":
                print(self.name + "运行结束！")
                return True
            T2 = time.time()
            # print(str(T1) + " , " + str(T2))
            self.keep_alive(T1, T2)
            print("这是" + self.name + "线程,当前设定的湿度为：" + str(self.s_humidity) + "，环境湿度：" + str(self.e_humidity) + "当前状态：" + str(self.state))
            time.sleep(self.delay)


thread1 = ac_thread(1, "空调1号", 10, 30, 26, "cool", 1, "", "KJ957H695Y", "503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb")
thread1.start()
thread2 = mon_thread(2, "摄像头1号", 10, "正常", "", "Q2NNW20813000326", "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
thread2.start()
thread3 = ac_thread(3, "空调2号", 10, 31, 24, "cool", 1, "", "FVFWD0WEHV29", "503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48df00")
thread3.start()
thread4 = ac_thread(4, "空调3号", 10, 31, 24, "cool", 1, "", "DMPCPUDPTRK", "503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48df01")
thread4.start()
thread5 = mon_thread(5, "摄像头2号", 10, "正常", "", "baydts4nnjjpvug", "503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48df10")
thread5.start()
