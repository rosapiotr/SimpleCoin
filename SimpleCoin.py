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

block_chain = Blockchain()
block1 = Block(1, ["11", "2"], 1, block_chain.last_block.block_hash)
block_chain.add_block(block1, block1.calcuate_block_hash())

block2 = Block(1, ["11", "2"], 1, block_chain.last_block.block_hash)
block_chain.add_block(block2, block2.calcuate_block_hash())

print("--------------------------------------------------------------")
print("Is blockchain valid: \t\t\t" + str(block_chain.check_integrity()))
print("--------------------------------------------------------------")
block_chain.chain[1].block_content["transaction_list"] = ["Changed list"]
print("Is blockchain after modification valid: " + str(block_chain.check_integrity()))
print("--------------------------------------------------------------")
