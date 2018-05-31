
import requests
import json
import web3
import time

#create persistent HTTP connection
session = requests.Session()
w3=web3.Web3()

#extracting data from the genesis file
PATH_GENESIS='./genesis.json'
genesisFile=json.load(open(PATH_GENESIS))
CHAINID=genesisFile['params']['networkID']
PERIOD=10
GASLIMIT=0x8000000


# +1 for each request
requestId=0

# mykey
myAddress='0xFB9C6fDB9232D91c6C70d301409eaF28203d3b96'
myPrivatekey='3c3c07e4bd52b4e4a6860c7ee1345118474edc2fc89de76f341abf0a6745f4e4'

# network address
URL='https://ropsten.infura.io/'

# define json objects
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

# get my nonce
requestObject, requestId = createJSONRPCRequestObject('eth_getTransactionCount',[myAddress,'latest'],requestId)

responseObject = postJSONRPCRequestObject(URL,requestObject)

myNonce = w3.toInt(hexstr=responseObject['result'])

print('nonce of address {} is {}'.format(myAddress,myNonce))



#create your transaction
a=True
while a:
    r_to=input('to address : ')
    r_amount=input('tx amount(wei) : ')
    if len(r_to) !=42 or r_to[0:2] != '0x':
        print('wrong address, please check recipient')
        try :
            amount=int(r_amount)
        except :
            print('wrong input value for tx amount')
            break;
    a=False
amount=int(r_amount)



transaction_dict = {'from':myAddress,'value':amount,'to':r_to,'chainId':CHAINID,'gasPrice':10**9,'gas':21000,'nonce':myNonce}

#sign the transaction
signed_transaction_dict = w3.eth.account.signTransaction(transaction_dict,myPrivatekey)
params=[signed_transaction_dict.rawTransaction.hex()]

#send the transaction to your node
requestObject,requestId = createJSONRPCRequestObject('eth_sendRawTransaction',params,requestId)
responseObject = postJSONRPCRequestObject(URL,requestObject)
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
            blockNumber = receipt['blockNumber']

            print('block number : {}'.format(blockNumber))
            print('{}wei sent to {} successfully!!'.format(amount,r_to))            
        else : 
            print(responseObject)
            raise ValueError('transacation status is "0x0", failed to deploy contract. Check gas, gasPrice first')
        break
    time.sleep(PERIOD)

#