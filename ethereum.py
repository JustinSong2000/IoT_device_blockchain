import sys
import json
import ECDSA
import hashlib
from eth_account.messages import encode_defunct
from eth_utils import decode_hex
from web3 import Web3, HTTPProvider
w3 = Web3(HTTPProvider('http://localhost:8545'))


#smart contract: abi, address and bytecode
config = {
	"abi":[
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "charge_convince",
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
		"inputs": [
			{
				"internalType": "string",
				"name": "a",
				"type": "string"
			}
		],
		"name": "checkreg",
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
		"name": "getBool",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
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
    "address":"0x77e3a99dE607D377B9A06E4DA7b138F001a6fF48"
}
#web3连接
contract = w3.eth.contract(address=config['address'], abi=config['abi'])
#使用ganache的第一个账户进行加密
# account = w3.eth.accounts[10]
# # account = w3.eth.accounts[0]
# print("账号为：" + account)
# # #sha3算法对一个语句进行加密，返回的是b'xxxx
# raw_msg = "test"
# shamsg = w3.sha3(text="test")
#
# # #将返回值转化成16进制，类型变为str，0x xxxx
# hashmsg = w3.toHex(shamsg)
# print("加密信息为：" + hashmsg)
# # #对数据进行签名
# # # print(decode_hex(shamesg))
# signedData = w3.eth.sign(account, hexstr=hashmsg)
# #签名返回转换成16进制表示
# signd = w3.toHex(signedData)
# print("签名为：" + signd)
# # #调用合约
#

# private = "1807111115601399896180711111560139989618071111156013998961807111"
# print(private)
# print(len(str(private)))
#
private_key = "1807111115601399896180711111560139989618071111156013998961807111"
# account = w3.eth.account.privateKeyToAccount(private_key)

wallet_private_key = "bff4961054b3f12b64e238bee1ef4d1487f172b988b0ca129c282188733892fb"  # 狐狸钱包的私钥
wallet_address = "0xa6aD1aeD4932E654205694f7e2dEf4BDd47DcF41"  # 狐狸钱包的公钥，就是钱包地址，是eth网络上的一个节点。

m = "a"
nonce = w3.eth.getTransactionCount(wallet_address)  # 这里要求出的是，哪个节点发起交易，就返回指定节点地址发起的交易数。
txn_dict = contract.functions.set_charge_convince(m).buildTransaction({
	'chainId': 3, #指测试网络
	'gas': 140000,
	'gasPrice': w3.toWei('40', 'gwei'),
	'nonce': nonce
})
signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)  # 这儿使用发起授权操作节点的私钥来签名
# 向网络发送交易信息
result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
# 准备接收发送回执
tx_receipt = w3.eth.getTransactionReceipt(result)



# #
# raw_msg = "test"
# eip_191_msg = encode_defunct(text=raw_msg)
# signed_message = w3.eth.account.sign_message(eip_191_msg, private_key=private_key)
#
# msg_hash = w3.toHex(signed_message.messageHash)
# shamsg = w3.sha3(text=eip_191_msg)
#
# # #将返回值转化成16进制，类型变为str，0x xxxx
# hashmsg = w3.toHex(shamsg)
# print("加密信息为：" + hashmsg)
# # msg_sig = w3.toHex(signed_message.signature)
#
# print("signed_message:\n", signed_message)
# print("msg_hash:\n", msg_hash)
# print("msg_sig:\n", msg_sig)
# print("expect recover address:\n", w3.eth.account.recover_message(eip_191_msg, signature=signed_message.signature))
#
# con = contract.functions.verify(msg_hash, msg_sig).call()
# print("签名者地址为：" + con)
# print(len(w3.eth.accounts))
# print(str(con) == account)
# print(contract.caller.)


# con = contract.functions.set_charge_convince(m).call()
# print(con)
con1 = contract.functions.get_convince().call()
print(con1)
# n = contract.functions.check_vir().call()
# print(n)
# print(w3.isConnected())
# # print(w3.eth.mining)
# print(con)
# txn_dict = contract.functions.set_charge_convince(m).buildTransaction({
#
# 	'chainId': 3,  # 指测试网络
#
# 	'gas': 140000,
#
# 	'gasPrice': w3.toWei('40', 'gwei'),
#
#
# })
# print(txn_dict)
# con1 = contract.functions.check_vir(m).call()
# print(con1)
# con = contract.functions.checkreg('KJ957H695Y').call()
# print(con)
# 0x0A071F0839572a365285Bd4B06B266777f3832fD
# print(con)
