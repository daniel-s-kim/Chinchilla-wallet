##for JSON request

#pip install requests

import requests

#create persistent HTTP connection
session = requests.Session()
print(session)

#as defined in https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version
method = 'net_version'
params = []
payload = {'jsonrpc':'2.0','method':method,'params':params,'id':1}

headers = {'Content-type':'application/json'}

#https://ropsten.infura.io/
#http://127.0.0.1:8545/
response = session.post('http://127.0.0.1:8545/',json=payload,headers=headers)

print('raw json response : {}'.format(response.json()))
print('network id : {}'.format(response.json()['result']))