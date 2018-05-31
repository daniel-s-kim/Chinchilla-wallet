#generate public & private key

import web3

ws = web3.Web3()

myAccount =ws.eth.account.create('chinchilla')
myAddress= myAccount.address
myPrivateKey = myAccount.privateKey

print('Address created : {}'.format(myAccount.address))
print('Private key for the wallet : {}'.format(myAccount.privateKey.hex()))


