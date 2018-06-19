#generate public & private key

import web3

w3 = web3.Web3()

myAccount =w3.eth.account.create('somekeys')
myAddress= myAccount.address
myPrivateKey = myAccount.privateKey

print('my address is : {}'.format(myAccount.address))
print('my private key is : {}'.format(myAccount.privateKey.hex()))


