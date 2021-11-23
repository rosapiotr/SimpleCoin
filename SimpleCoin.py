import hashlib
import json
import time

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
    def __init__(self):
        self.chain = []
        self.create_first_block()
 
    def create_first_block(self):
        first_block = Block(0, [], time.time(), "0")
        first_block.hash = first_block.calcuate_block_hash()
        self.chain.append(first_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        previous_hash = self.last_block.block_hash
        if previous_hash != block.block_content["previous_hash"]:
            print("Failed to add a new block")
            return False
        block.block_hash = proof
        self.chain.append(block)
        return True

    def check_integrity(self):
        for i in range(1, len(self.chain)):
            if self.chain[i-1].block_hash != self.chain[i].block_content["previous_hash"] or self.chain[i].block_hash != self.chain[i].calcuate_block_hash():
                return False
        return True

def generate_SimpleCoins_for_all_users():
    block = Block(1,["admin","Kamil",1],1,block_chain.last_block.block_hash)
    block_chain.add_block(block,block.calcuate_block_hash())
    block = Block(1,["admin","Zofia",2],1,block_chain.last_block.block_hash)
    block_chain.add_block(block,block.calcuate_block_hash())
    block = Block(1,["admin","Piotr",3],1,block_chain.last_block.block_hash)
    block_chain.add_block(block,block.calcuate_block_hash())
    block = Block(1,["admin","Ala",4],1,block_chain.last_block.block_hash)
    block_chain.add_block(block,block.calcuate_block_hash())
    block = Block(1,["admin","Ola",5],1,block_chain.last_block.block_hash)
    block_chain.add_block(block,block.calcuate_block_hash())
    print("Generation completed!")

def new_transaction(address_from,address_to,coin_number):
    if block_chain.check_integrity():
        anti_double_spending = 0
        for i in range(1,len(block_chain.chain)):
            if block_chain.chain[i].block_content["transaction_list"][1] == address_from and block_chain.chain[i].block_content["transaction_list"][2] == coin_number:
                anti_double_spending = anti_double_spending + 1
            if block_chain.chain[i].block_content["transaction_list"][0] == address_from and block_chain.chain[i].block_content["transaction_list"][2] == coin_number:
                anti_double_spending = anti_double_spending - 1
        if anti_double_spending == 1 and address_from != address_to:
            block = Block(1,[address_from,address_to,coin_number],1,block_chain.last_block.block_hash)
            block_chain.add_block(block,block.calcuate_block_hash())
            print("Transaction from " + address_from + " to " + address_to + " was successful!")
        if anti_double_spending != 1 and address_from != address_to:
            print(address_from + ", you don't have coin number: " + str(coin_number))
        if address_from == address_to:
            print(address_from + ", you can't send coin to yourself!")
    else:
        print("No chain integrity!")

def check_balance(person):
    balance = 0
    for i in range(1,len(block_chain.chain)):
        if block_chain.chain[i].block_content["transaction_list"][1] == person:
            balance = balance + 1
    for i in range(1,len(block_chain.chain)):
        if block_chain.chain[i].block_content["transaction_list"][0] == person:
            balance = balance - 1
    print(person + "'s balance is " + str(balance) + " SC!")
    return balance

block_chain = Blockchain()
generate_SimpleCoins_for_all_users()
new_transaction("Kamil","Zofia",1)
check_balance("Kamil")
check_balance("Zofia")
new_transaction("Zofia","Kamil",1)
check_balance("Kamil")
check_balance("Zofia")
new_transaction("Zofia","Kamil",1)
check_balance("Kamil")
check_balance("Zofia")
new_transaction("Kamil","Kamil",1)
check_balance("Kamil")