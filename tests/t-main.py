
import requests
import json
import web3
import pprint
import time

#create persistent HTTP connection
session = requests.Session()
w3=web3.Web3()
pp=pprint.PrettyPrinter(indent=2)

requestId=0 # is automatically incremented at each request

#'https://ropsten.infura.io/'
#'http://localhost:8545/'
URL='https://ropsten.infura.io/'
PATH_GENESIS='./genesis.json'
PATH_SC_TRUFFLE='./truffle/'

#extracting data from the genesis file
genesisFile=json.load(open(PATH_GENESIS))
CHAINID=genesisFile['params']['networkID']
PERIOD=300
GASLIMIT=0x8000000

#compile your contract with truffle first
r'''
do
truffle init
//add the smart contract in contracts/
truffle compile'''
truffleFile=json.load(open(PATH_SC_TRUFFLE+'/build/contracts/Migrations.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

#mykey
myAddress='0xFB9C6fDB9232D91c6C70d301409eaF28203d3b96' #address funded in genesis file
myPrivatekey='3c3c07e4bd52b4e4a6860c7ee1345118474edc2fc89de76f341abf0a6745f4e4'

####################################################
#see http://www.jsonrpc.org/specification
#and https://github.com/ethereum/wiki/wiki/JSON-RPC

def createJSONRPCRequestObject(_method,_params,_requestId):
    return{
        'jsonrpc':'2.0',
        'method':_method,
        'params':_params,
        'id':_requestId
    },_requestId+1

def postJSONRPCRequestObject(_HTTPnpoint,_jsonRPCRequestObject):
    response = session.post(_HTTPnpoint,json=_jsonRPCRequestObject,headers={'Content-type':'application/json'})

    return response.json()

##deploy smart contract
#get your nonce

requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionCount',[myAddress,'latest'],requestId)

responseObject = postJSONRPCRequestObject(URL,requestObject)

myNonce = w3.toInt(hexstr=responseObject['result'])

print('nonce of address {} is {}'.format(myAddress,myNonce))

#create your transaction
transaction_dict = {'from':myAddress,'to':'','chainId':CHAINID,'gasPrice':1,'gas':2000000,'nonce':myNonce,'data':bytecode}

#sign the transaction
signed_transaction_dict = w3.eth.account.signTransaction(transaction_dict,myPrivatekey)
params=[signed_transaction_dict.rawTransaction.hex()]

#send the transaction to your node
requestObject,requestId = createJSONRPCRequestObject('eth_sendRawTransaction',params,requestId)
responseObject = postJSONRPCRequestObject(URL,requestObject)
print(responseObject)
transactionHash = responseObject['result']
print('contract submission hash {}'.format(transactionHash))

#wait for the transaction to be mined and get the address of the new contract
while (True):
    requestObject,requestId = createJSONRPCRequestObject('eth_getTransactionReceipt',[transactionHash],requestId)
    responseObject = postJSONRPCRequestObject(URL,requestObject)
    receipt = responseObject['result']
    if receipt is not None :
        if receipt['status'] == '0x1':
            contractAddress = receipt['contractAddress']
            print('newly deployed contract at address {}'.format(contractAddress))
        else : 
            pp.print(responseObject)
            raise ValueError('transacation status is "0x0", failed to deploy contract. Check gas, gasPrice first')
        break
    time.sleep(PERIOD/10)

#### Send a transaction to smart contract

#get your nonce
requestObject,requestId = createJSONRPCRequestObject('eth_getTransactoinCount',[myAddress,'latest'],requestId)
responseObject = postJSONRPCRequestObject(URL,requestObject)
myNonce=w3.toInt(hexstr=responseObject['result'])
print('nonce of address {} is {}'.format(myAddress,myNonce))

##prepare the data field of the transaction
#function selector and argument encoding
#https://solidity.readthedocs.io/en/develop/abi-spec.html#function-selector-and-argument-encoding

value1, value2 = 10, 32 #random numbers here
function = 'add(uint256,uint256)' #from smart contract
methodId = w3.sha3(text=function)[0:4]
param1 = (value1).to_bytes(32,byteorder='big').hex()
param2 = (value2).to_bytes(32,byteorder='big').hex()
data='0x'+methodId+param1+param2

transaction_dict = {'from':myAddress,'to':contractAddress,'chainId':CHAINID,'gasPrice':1,'gas':200000,'nonce':myNonce,'data':data}

#sign the transaction
signed_transaction_dict=w3.eth.account.signTransaction(transaction_dict,myPrivatekey)
params = [signed_transaction_dict.rawTransaction.hex()]

#send the transaction to your node
print('executing {} with value {},{}'.format(function,value1,value2))
requestObject, requestId = createJSONRPCRequestObject('eth_sendRawTransaction',params,requestId)
responseObject = postJSONRPCRequestObject(URL,requestObject)
transactionHash = responseObject['result']
print('transaction hash {}'.format(transactionHash))

#wait for the transaction to be mined
while True :
    requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionReceipt',[transactionHash],requestId)
    responseObject = postJSONRPCRequestObject(URL,requestObject)
    receipt = responseObject['result']
    if receipt is not None :
        if receipt['status'] == '0x1' :
            print('transaction sucessfully mined')
        else :
            pp.pprint(responseObject)
            raise ValueError('transaction status is "0x0", failed to deploy contract. Check gas, gas price first.')
        break;
    time.sleep(PERIOD/10)


### Read your smart contract state using geth
# we don't need a nonce since this does not create a transaction but only ask our node to read it's local database

## prepare the data field of the transaction
# function selector and argument encoding
# https://solidity.readthedocs.io/en/develop/abi-spec.html#function-selector-and-argument-encoding
# state is declared as public in the smart contract. This creates a getter function

methodId = w3.sha(text='state()')[0:4].hex()
data = '0x'+ methodId
transaction_dict = {'from':myAddress,'to':contractAddress,'chainId':CHAINID,'data':data}
params=[transaction_dict,'latest']
requestObject,requestId=createJSONRPCRequestObject('eth_call',params,requestId)
responseObject=postJSONRPCRequestObject(URL,requestObject)
state=w3.toInt(hexstr=responseObject['result'])
print('using geth for public variables: result is {}'.format(state))

### Read your smart contract state get functions
# we don't need a nonce since this does not create a transaction but only ask out node to read it's local database

## prepare the data field of the transaction
# function selector and argument encoding
# https://solidity.readthedocs.io/en/develop/abi-spec.html#function-selector-and-argument-encoding
# state is declared as public in the smart contract. This creates a getter function

methodId = w3.sha3(text='getState()')[0:4].hex()
data = '0x'+methodId
transaction_dict = {'from':myAddress,'to':contractAddress,'chainId':CHAINID,'data':data}
params=[transaction_dict,'latest']
requestObject,requestId=createJSONRPCRequestObject('eth_call',params,requestId)
responseObject=postJSONRPCRequestObject(URL,requestObject)
state = w3.toInt(hexstr=responseObject['result'])
print('using getState() function: result is {}'.format(state))

