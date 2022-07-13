
ganache-cli
geth attach http://localhost:8545

项目有空调，摄像头，扫地机器人（未完成）

1 正常设备一空调1号
personal.importRawKey("0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48dfcb", 'passwd')

2 正常设备二摄像头1号
personal.importRawKey("0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", 'passwd')

3 异常设备一空调2号 使用未经允许的序列号
personal.importRawKey("0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48df00", 'passwd')

4 异常设备二空调3号 注册成功，签名认证未通过
personal.importRawKey("0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48df01", 'passwd')

5 异常设备三摄像头2号 注册成功，但是使用另一设备的Token发起接入
personal.importRawKey("0x503f38a9c967ed597e47fe25643985f032b072db8075426a92110f82df48df10", 'passwd')
使用设备一的Token
0x61c8d6cbebc2e1678857522ee893b599651a2fbd48eadcfef62b282b1ef5f9c2574508c43a0e44d976f24adc49884e1988fb5e8d7584733b4833be43027c0ed01b

CA密钥
personal.importRawKey("0x1807111115601399896180711111560139989618071111156013998961807111", 'passwd')