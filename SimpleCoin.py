import base64
import binascii
import hashlib
import json
import time
from urllib import response
import ecdsa
from numpy import block
import random

class Block:
    def __init__(self, index, transaction_list, timestamp, previous_hash, nonce=0):
        self.block_content = {
            "index": index,
            "transaction_list": transaction_list,
            "nonce": nonce,
            "timestamp": timestamp,
            "previous_hash": previous_hash
        }
        self.block_hash = self.calcuate_block_hash()

    def calcuate_block_hash(self):
        return hashlib.sha256(json.dumps(self.block_content, sort_keys=True).encode()).hexdigest()


class Blockchain:
    def __init__(self, blockchain_wallet):
        self.chain = []
        self.current_transactions = []
        self.wallets = []
        self.bc_wallet = blockchain_wallet

    @property
    def last_block(self):
        return self.chain[-1]

    def mine(self, difficulty_bits = 4):
        if not self.current_transactions:
            return False

        new_block = Block(self.last_block.block_content["index"] + 1, self.current_transactions, timestamp=time.time(),
                          previous_hash=self.last_block.block_hash)

        while not new_block.calcuate_block_hash().startswith(difficulty_bits*'0'):
            new_block.block_content["nonce"] += 1
        new_block.block_hash = new_block.calcuate_block_hash()
        self.add_block(new_block, new_block.block_hash)
        self.current_transactions = []
        return True

    def add_block(self, block, proof):
        previous_hash = self.last_block.block_hash
        if previous_hash != block.block_content["previous_hash"] or block.block_hash != proof:
            print("Failed to add a new block")
            return False
        self.chain.append(block)
        return True

    def add_genesis_block(self, block):
        self.chain.append(block)
        return True

    def check_integrity(self):
        for i in range(1, len(self.chain)):
            # check if signatures in all blocks are valid
            for transaction in self.chain[i].block_content["transaction_list"]:
                if not self.validate_signature(transaction=transaction):
                    print("Signature does not match in transaction " + str(transaction))
                    return False
            # check if previous_hash equals to block_hash and if block_hash is equal to actual hash
            if self.chain[i-1].block_hash != self.chain[i].block_content["previous_hash"] or self.chain[i].block_hash != self.chain[i].calcuate_block_hash():
                print("Blockchain is not valid")
                return False
            
        return True

    def add_wallet(self, wallet):
        self.wallets.append(wallet)

    def new_transaction(self, sender, recipient, coin_id):
        transaction = {
            'sender': sender.public_key,
            'recipient': recipient.public_key,
            'coin_id': coin_id
        }
        transaction["signature"] = sender.sign_transaction(transaction)
        if self.validate_transaction(transaction):
            print("Transaction: Coin with ID " + str(transaction["coin_id"]) + ", from " + str(transaction["sender"]) +
                  " to " + str(transaction["recipient"]) + " was successful!")
            self.current_transactions.append(transaction)
            return transaction
        else:
            print("You (ID: " + str(transaction["sender"]) +
                  ") don't have coin with ID: " + str(transaction["coin_id"]))
            return None

    def validate_signature(self, transaction):
        transaction_copy = transaction.copy()
        public_key = transaction_copy["sender"]
        signature_encoded = transaction_copy.pop("signature", None)
        if signature_encoded is None:
            print("The transaction is not signed")
            return False
        try:
            signature = base64.b64decode(signature_encoded)
        except binascii.Error:
            return False
        signature = base64.b64decode(signature_encoded)
        transaction_copy_bytes = self.transaction_to_bytes(transaction_copy)
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)

        if not vk.verify(signature, transaction_copy_bytes):
            print("Signature does not match the transaction")
            return False
        return True

    def validate_initial_coins(self):
        for transaction in self.chain[0].block_content["transaction_list"]:
            # check if sender in initial block is blockchain
            if transaction["sender"] != self.bc_wallet.public_key :
                print("Sender is not BLOCKCHAIN in initial block in transaction: " + str(transaction))
                return False
            # validity of signatures in initial block
            if not self.validate_signature(transaction=transaction):
                    print("Signature does not match in transaction " + str(transaction))
                    return False
        return True

    def validate_transaction(self, transaction):
        if transaction["sender"] == transaction["recipient"]:
            print("You can't send coin to yourself!")
            return False
        if not self.validate_signature(transaction):
            return False
        does_have_coin_id = False
        for i in range(0, len(self.chain)):
            transaction_list_in_loop = self.chain[i].block_content["transaction_list"]
            for j in range(0, len(transaction_list_in_loop)):
                if transaction_list_in_loop[j]["recipient"] == transaction["sender"] and transaction_list_in_loop[j]["coin_id"] == transaction["coin_id"]:
                    does_have_coin_id = True
                if transaction_list_in_loop[j]["sender"] == transaction["sender"] and transaction_list_in_loop[j]["coin_id"] == transaction["coin_id"]:
                    does_have_coin_id = False
        for i in range(0, len(self.current_transactions)):
            if self.current_transactions[i]["recipient"] == transaction["sender"] and self.current_transactions[i]["coin_id"] == transaction["coin_id"]:
                does_have_coin_id = True
            if self.current_transactions[i]["sender"] == transaction["sender"] and self.current_transactions[i]["coin_id"] == transaction["coin_id"]:
                does_have_coin_id = False
        return does_have_coin_id

    def check_balance(self, wallet_public_key):
        coin_ids = set()
        for i in range(0, len(self.chain)):
            transaction_list_in_loop = self.chain[i].block_content["transaction_list"]
            for j in range(0, len(transaction_list_in_loop)):
                if transaction_list_in_loop[j]["recipient"] == wallet_public_key:
                    coin_ids.add(transaction_list_in_loop[j]["coin_id"])
                elif transaction_list_in_loop[j]["sender"] == wallet_public_key:
                    coin_ids.discard(transaction_list_in_loop[j]["coin_id"])
        for i in range(0, len(self.current_transactions)):
            if transaction_list_in_loop[j]["recipient"] == wallet_public_key:
                coin_ids.add(transaction_list_in_loop[j]["coin_id"])
            elif transaction_list_in_loop[j]["sender"] == wallet_public_key:
                coin_ids.discard(transaction_list_in_loop[j]["coin_id"])
        balance = len(coin_ids)
        print("Selected wallet (ID: " + str(wallet_public_key) + ") owns " + str(balance) +
              " SimpleCoin(s): " + str(sorted(coin_ids)))
        return coin_ids

    def transaction_to_bytes(self, transaction):
        return json.dumps(transaction, sort_keys=True).encode()


class Wallet:

    def __init__(self, name):
        self.name = name
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.__private_key = sk.to_string().hex()
        vk = sk.get_verifying_key()
        self.public_key = vk.to_string().hex()

    def sign_transaction(self, transaction):
        transaction_bytes = self.transaction_to_bytes(transaction)
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(self.__private_key), curve=ecdsa.SECP256k1)
        signature = base64.b64encode(sk.sign(transaction_bytes)).decode("utf-8")
        return signature

    def transaction_to_bytes(self, transaction):
        return json.dumps(transaction, sort_keys=True).encode()

class User:

    def __init__(self, name, blockchain_wallet):
        self.name = name
        self.wallet = Wallet(name)
        self.blockchain = Blockchain(blockchain_wallet)
        self.nodes = []
    
    def add_node(self, node):
        self.nodes.append(node)

    def new_transaction(self, recipient_wallet, coin_id): 
        transaction = self.blockchain.new_transaction(self.wallet, recipient_wallet, coin_id)
        if transaction is not None:
            for node in self.nodes:
                if random.random() < 0.9:
                    if node.blockchain.validate_transaction(transaction):
                        node.blockchain.current_transactions.append(transaction)
                    else: 
                        print("Node " + node.name + " did not accept a transaction")
            return True
        return False


def generate_genesis_block(users):
    initial_transactions = []
    coin_counter = 1
    for user in users:
        initialTransaction = {
            "sender": users[user].blockchain.bc_wallet.public_key,
            "recipient": users[user].wallet.public_key,     # Kamil
            "coin_id": coin_counter
        }
        initialTransaction["signature"] = users[user].blockchain.bc_wallet.sign_transaction(initialTransaction)
        coin_counter += 1
        initial_transactions.append(initialTransaction)

    block = Block(0, initial_transactions, time.time(), "0")
    return block

blockchain_wallet = Wallet("BLOCKCHAIN")
users = {
    "Kamil": User("Kamil", blockchain_wallet),
    "Piotr": User("Piotr", blockchain_wallet),
    "Zofia": User("Zofia", blockchain_wallet)
}

genesis_block = generate_genesis_block(users)

for user in users:
    users[user].blockchain.add_genesis_block(genesis_block)

users["Piotr"].blockchain.check_balance(users["Piotr"].wallet.public_key)
users["Piotr"].blockchain.check_balance(users["Kamil"].wallet.public_key)
users["Zofia"].blockchain.check_balance(users["Zofia"].wallet.public_key)

for user in users:
    for userNode in users:
        if user != userNode:
            users[user].add_node(users[userNode])

users["Piotr"].new_transaction(users["Kamil"].wallet, 2)     # walletPiotr sends Coin 1 to walletKamil
users["Zofia"].new_transaction(users["Kamil"].wallet, 3)     # walletPiotr sends Coin 1 to walletKamil

print("----")
users["Piotr"].blockchain.mine()    # make it run in parallel 


# blockchain.new_transaction(walletPiotr, walletKamil, 2)     # walletPiotr sends Coin 2 to walletKamil
# blockchain.new_transaction(walletZofia, walletKamil, 3)     # walletZofia sends Coin 3 to walletKamil
# print("----")
# blockchain.mine()
# blockchain.check_balance(walletKamil.public_key)
# blockchain.check_balance(walletPiotr.public_key)
# blockchain.check_balance(walletZofia.public_key)
# print("----")

