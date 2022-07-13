import ECDSA
import pub
import json
import sys
import os
import time
import paho.mqtt.client as mqtt
from web3 import Web3, HTTPProvider
from eth_account.messages import encode_defunct

w3 = Web3(HTTPProvider('http://localhost:8545'))

#CA在这里生成了自己的私钥
# CA_sk, CA_pk = ECDSA.make_keypair()
CA_sk = "1807111115601399896180711111560139989618071111156013998961807111"
CA_pk = w3.eth.accounts[len(w3.eth.accounts) - 1]

config = {
	"abi": [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "b",
				"type": "string"
			}
		],
		"name": "check_charge_device",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "b",
				"type": "string"
			}
		],
		"name": "check_convince",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "b",
				"type": "string"
			}
		],
		"name": "check_vir",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "get_charge_convince",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "get_charge_device",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "get_convince",
		"outputs": [
			{
				"internalType": "string[]",
				"name": "",
				"type": "string[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getverifymsg",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "a",
				"type": "string"
			}
		],
		"name": "set_charge_convince",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "a",
				"type": "string"
			}
		],
		"name": "set_charge_device",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "a",
				"type": "string"
			}
		],
		"name": "set_convince",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "hash",
				"type": "bytes32"
			},
			{
				"internalType": "bytes",
				"name": "sig",
				"type": "bytes"
			}
		],
		"name": "verify",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "hash",
				"type": "bytes32"
			},
			{
				"internalType": "uint8",
				"name": "v",
				"type": "uint8"
			},
			{
				"internalType": "bytes32",
				"name": "r",
				"type": "bytes32"
			},
			{
				"internalType": "bytes32",
				"name": "s",
				"type": "bytes32"
			}
		],
		"name": "verifyComplex",
		"outputs": [
			{
				"internalType": "address",
				"name": "retAddr",
				"type": "address"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	}
],
	"address": '0x39FCa747649e9548374e586f08268a1c356e4536'
}

w3.eth.defaultAccount = w3.eth.accounts[0]
contract = w3.eth.contract(address=config['address'],abi=config['abi'])

verify_switch = False
count = 0 			####计数用，CA只需要写入一次即可

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")
reg_List = []
reg_reject_List = []
verify_list = []
final_list = []
trust_list = []
final_reject_list = []

REPORT_TOPIC1 = 'deregister'  # 注册主题
REPORT_TOPIC2 = 'verify'  # 认证主题
REPORT_TOPIC3 = 'state'  # 状态主题


filename = 'Edge.txt'
with open(filename, 'w') as f:
	f.write('')

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


def on_connect(client, userdata, flags, rc):
	# print('connected to mqtt with resurt code ', rc)
	# client.subscribe(REPORT_TOPIC1)  # 注册主题
	client.subscribe('register')  # 注册主题
	client.subscribe(REPORT_TOPIC2)  # 认证主题
	client.subscribe(REPORT_TOPIC3)  # 状态主题
	print("边缘节点成功启动！")


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
	with open(filename, 'a') as f:
		if payload['cmd'] == 'deregister' and payload['id'] not in reg_List and payload['id'] not in reg_reject_List and payload['id'] not in final_list:
			f.write(str(payload) + '\n')
			con = contract.functions.check_convince(payload['id']).call()
			if con == True:
				pub.clicent_main("设备序列号为" + payload['id'] + "    confirm_register!   ", payload['id'], "register")
				reg_List.append(payload['id'])
			else:
				pub.clicent_main("设备序列号为" + payload['id'] + "    reject！！   ", payload['id'], "register")
				reg_reject_List.append(payload['id'])
		if str(payload).find("verify_start") != -1 and payload['id'] in reg_List and payload['id'] not in verify_list:
			f.write(str(payload) + '\n')
			v_msg = contract.functions.getverifymsg().call()
			pub.clicent_main(v_msg, payload['id'], "verify")
			verify_list.append(payload['id'])
		if 'shake' in str(payload) and payload['id'] not in final_list and payload['id'] not in final_reject_list:
			f.write(str(payload) + '\n')
			a = payload['id']
			###这里想一下设备的公钥私钥怎么生成
			##设备应该使用ganache中的账户对数据进行加密
			# print(a['address'])
			b = payload['msg']
			# print("b = " + b)
			msg_hash, msg_sig = my_inverse(b)
			msg_hash = msg_hash.strip("'")
			msg_sig = msg_sig.strip("'")
			ret_account = contract.functions.verify(msg_hash, msg_sig).call()
			# print(ret_account)
			if ret_account == a:
				verify_result = 'signature matches'
			else:
				verify_result = 'invalid signature'
			print(payload['id'] + "明文验证结果为: " + verify_result)
			if verify_result == 'signature matches':
				#这里应该是将设备写进智能合约里的信任列表中
				nonce = w3.eth.getTransactionCount(CA_pk)  # 这里要求出的是，哪个节点发起交易，就返回指定节点地址发起的交易数。
				txn_dict = contract.functions.set_charge_convince(payload['id']).buildTransaction({
					'chainId': 3,  # 指测试网络
					'gas': 140000,
					'gasPrice': w3.toWei('40', 'gwei'),
					'nonce': nonce
				})
				signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=CA_sk)  # 这儿使用发起授权操作节点的私钥来签名
				# 向网络发送交易信息
				result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
				# 准备接收发送回执
				tx_receipt = w3.eth.getTransactionReceipt(result)
				# print(tx_receipt)
				final_list.append(payload['id'])
				raw_msg = a
				eip_191_msg = encode_defunct(text=raw_msg)
				Token = w3.eth.account.sign_message(eip_191_msg, private_key=CA_sk)
				sig_Token = w3.toHex(Token.signature)

				# print(message_hash)
				# print(sig_Token)
				pub.clicent_main("验证结果：" + verify_result, payload['id'], "shake_result")
				pub.clicent_main(sig_Token, payload['id'], "certification")
			else:
				pub.clicent_main("验证结果：" + verify_result, payload['id'], "shake_result")
				final_reject_list.append(payload['id'])
		################设备接入过程################
		if payload['cmd'] == 'deregister' and payload['id'] in final_list:
			con = contract.functions.check_vir(payload['id']).call()
			if con == True:
				f.write(str(payload) + '\n')
				# print(payload)
				trust_list.append(payload['id'])
			else:
				print(payload['id'] + "接入失败！")
		##########
		####边缘节点中维护这样几个表：
		#最开始的信任表
		#注册成功的表
		#接入成功表
		if payload['cmd'] == 'access_require' and payload['id'] in trust_list:
			f.write("设备：" + payload['id'] + "开始接入认证" + '\n')
			f.write(str(payload) + '\n')
			# 检查设备的公钥是否在最终列表中
			pub.clicent_main("验证结果：success!", payload['id'], "access_confirm")
		if payload['cmd'] == 'access_shake':
			f.write(str(payload) + '\n')
			# eip_191_msg = encode_defunct(text=payload['id'])
			eip_191_msg = encode_defunct(text=payload['id'])
			Token = w3.eth.account.sign_message(eip_191_msg, private_key=CA_sk)
			# print(type(Token))
			# print(Token)
			# Token = payload['msg']
			# print(Token)
			sign_token = payload['msg'] 		##得到的Token
			sig_Token = w3.toHex(Token.signature) #计算出的Token
			message_hash = w3.toHex(Token.messageHash)
			# print(message_hash + ", " + sign_token)
			acc = contract.functions.verify(message_hash, sign_token).call()
			# print(acc)
			# print(payload['id'])
			# print(CA_pk)
			if acc == CA_pk and sig_Token == sign_token:
				pub.clicent_main("验证结果：success!", payload['id'], "certification_match")
			# if ECDSA.check_certification(de_pk, CA_sk, certification):
			# 	pub.clicent_main("验证结果：success!", payload['id'], "certification_match")
			# 	verify_msg = "18071111_SYX"
			# 	pub.clicent_main(verify_msg, payload['id'], "access_verify")
				nonce = w3.eth.getTransactionCount(CA_pk)  # 这里要求出的是，哪个节点发起交易，就返回指定节点地址发起的交易数。
				txn_dict = contract.functions.set_charge_device(payload['msg']).buildTransaction({
					'chainId': 3,  # 指测试网络
					'gas': 500000,
					'gasPrice': w3.toWei('40', 'gwei'),
					'nonce': nonce
				})
				signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=CA_sk)  # 这儿使用发起授权操作节点的私钥来签名
				# 向网络发送交易信息
				result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
				# 准备接收发送回执
				tx_receipt = w3.eth.getTransactionReceipt(result)
				if count == 0:
					_convince = contract.functions.get_convince().call()
					charge_convince = contract.functions.get_charge_convince().call()
					charge_device = contract.functions.get_charge_device().call()
					f.write("注册授权列表： " + str(_convince) + '\n')
					f.write("接入允许列表： " + str(charge_convince) + '\n')
					f.write("接入成功的设备： " + str(charge_device) + '\n')
					########这里让CA只写一次就行
			# print(tx_receipt)
			else:
				pub.clicent_main("验证结果：fail!", payload['id'], "invalid_certification")
				print(payload['id'] + "接入认证失败！")


def server_conenet(client):
	client.on_connect = on_connect  # 启用订阅模式
	client.on_message = on_message  # 接收消息
	client.connect("127.0.0.1", 1883, 60)  # 链接
	# client.loop_start()  # 以start方式运行，需要启动一个守护线程，让服务端运行，否则会随主线程死亡
	client.loop_forever()  # 以forever方式阻塞运行。


def server_stop(client):
	client.loop_stop()  # 停止服务端
	sys.exit(0)


def server_main():
	client_id = '18071111_SYX'
	client = mqtt.Client(client_id, transport='tcp')
	# pub.clicent_main("ok", str(CA_pk), "register")
	server_conenet(client)


#给一个设备发布公钥和私钥
def deliver_key():
	return ECDSA.make_keypair()


def my_inverse(a):
	b = ''
	c = ''
	i = 1
	while a[i] != ',':
		b = b + a[i]
		i = i + 1

	i = i + 2

	while a[i] != ']':
		c = c + a[i]
		i = i + 1

	return  b,c

#给一个设备数字证书
def digital_certification(d_pk):
	d_dc = ECDSA.scalar_mult(CA_sk, d_pk)
	return d_dc


if __name__ == '__main__':
	server_main()

# print(deliver_key())
# d_sk, d_pk = deliver_key()
# print(CA_sk)
# print(d_pk)
# print(str(d_pk) + ", " + str(d_sk))
# print(digital_certification(d_pk))
# msg = b'hello'
# signiture = ECDSA.sign_message(CA_sk, msg)
# print(ECDSA.verify_signature(CA_pk, msg, signiture))