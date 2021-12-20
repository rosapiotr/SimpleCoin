import base64
import hashlib
import json
import time
import ecdsa

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
        self.current_transactions = []
        self.wallets = []
        self.create_first_block()
        self.initiateResources()

    def create_first_block(self):
        first_block = Block(0, [], time.time(), "0")
        self.chain.append(first_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def mine(self):
        if not self.current_transactions:
            return False

        new_block = Block(self.last_block.block_content["index"] + 1, self.current_transactions, timestamp=time.time(),
                          previous_hash=self.last_block.block_hash)

        while not new_block.calcuate_block_hash().startswith('00'):
            new_block.block_content["nonce"] += 1
        new_block.block_hash = new_block.calcuate_block_hash()
        self.add_block(new_block, new_block.block_hash)
        self.unconfirmed_transactions = []
        return True

    def add_block(self, block, proof):
        previous_hash = self.last_block.block_hash
        if previous_hash != block.block_content["previous_hash"] or block.block_hash != proof:
            print("Failed to add a new block")
            return False
        self.chain.append(block)
        return True

    def check_integrity(self):
        for i in range(1, len(self.chain)):
            if self.chain[i-1].block_hash != self.chain[i].block_content["previous_hash"] or self.chain[i].block_hash != self.chain[i].calcuate_block_hash():
                return False
        return True

    def add_wallet(self, wallet):
        self.wallets.append(wallet)

    def new_transaction(self, sender_public_key, sender_private_key, recipient_public_key, coin_id):
        transaction = {
            'sender': sender_public_key,
            'recipient': recipient_public_key,
            'coin_id': coin_id
        }
        transaction["signature"] = self.sign_transaction(transaction, sender_private_key)
        if self.validate_transaction(transaction):
            self.current_transactions.append(transaction)
            return True
        return False

    def validate_transaction(self, transaction):
        transaction_copy = transaction.copy()
        public_key = (base64.b64decode(transaction_copy["sender"])).hex()
        signature_encoded = transaction_copy.pop("signature", None)
        if signature_encoded is None:
            print("The transaction is not signed")
            return False
        signature = base64.b64decode(transaction_copy["signature"])
        transaction_copy_bytes = self.transaction_to_bytes(transaction_copy)
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)

        if not vk.verify(transaction_copy_bytes, signature, public_key):
            print("Signature does not match the transaction")
            return False
        if transaction["sender"] == transaction["recipient"]:
            print("You can't send coin to yourself!")
            return False
        # changed from int 0 because if chain is vaild, during check it can only take value 0 or 1
        does_have_coin_id = False
        for i in range(1, len(self.chain)):
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
        if does_have_coin_id:
            print("Transaction: Coin with ID " + str(transaction["coin_id"]) + ", from " + str(transaction["sender"]) +
                  " to " + str(transaction["recipient"]) + " was successful!")
        else:
            print("You (ID: " + str(transaction["sender"]) +
                  ") don't have coin with ID: " + str(transaction["coin_id"]))
        return does_have_coin_id

    def check_balance(self, wallet_public_key):
        coin_ids = set()
        for i in range(1, len(self.chain)):
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

    def sign_transaction(self, transaction, private_key):
        print(transaction)
        transaction_bytes = self.transaction_to_bytes(transaction)
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        signature = base64.b64encode(sk.sign(transaction_bytes))
        return signature

    def create_sample_wallets(self):
        walletKamil = Wallet("Kamil")
        walletPiotr = Wallet("Piotr")
        walletZofia = Wallet("Zofia")
        self.add_wallet(walletKamil)
        self.add_wallet(walletPiotr)
        self.add_wallet(walletZofia)

    def generate_SimpleCoins_for_all_wallets(self):
        initialTransaction1 = {
            "sender": 0,
            "recipient": 1,     # Kamil
            "coin_id": 1
        }
        initialTransaction2 = {
            "sender": 0,
            "recipient": 2,     # Piotr
            "coin_id": 2
        }
        initialTransaction3 = {
            "sender": 0,
            "recipient": 3,     # Zofia
            "coin_id": 3
        }
        block = Block(self.last_block.block_content["index"] + 1,
                      [initialTransaction1, initialTransaction2, initialTransaction3], time.time(), self.last_block.block_hash)
        self.add_block(block, block.block_hash)
        print("Generation completed!")

    def initiateResources(self):
        self.create_sample_wallets()
        self.generate_SimpleCoins_for_all_wallets()

class Wallet:

    def __init__(self, name):
        self.name = name
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.private_key = sk.to_string().hex()
        vk = sk.get_verifying_key()
        self.public_key = base64.b64encode(bytes.fromhex(vk.to_string().hex()))
        print("Public key: " + str(self.public_key))


blockchain = Blockchain()
blockchain.check_balance(1)
blockchain.check_balance(2)
blockchain.check_balance(3)
print("----")

walletKamil = blockchain.wallets[0]
walletPiotr = blockchain.wallets[1]
walletZofia = blockchain.wallets[2]

print(walletKamil.public_key)

blockchain.new_transaction(walletKamil.public_key, walletKamil.public_key, walletPiotr.public_key, 1)     # User 1 sends Coin 1 to User 2
# blockchain.new_transaction(1, 2, 1)     # User 1 sends Coin 1 to User 2 again - error
# blockchain.new_transaction(2, 1, 1)     # User 2 sends Coin 1 to User 1
# blockchain.new_transaction(2, 1, 1)     # User 2 sends Coin 1 to User 1 again - error
# blockchain.new_transaction(2, 1, 2)     # User 2 sends Coin 2 to User 1
# # blockchain.new_transaction(1, 2, 1)     # User 1 sends Coin 1 to User 2
# # blockchain.new_transaction(1, 2, 2)     # User 1 sends Coin 2 to User 2
# print("----")
# blockchain.mine()
# blockchain.check_balance(1)
# blockchain.check_balance(2)
# blockchain.check_balance(3)

# print("Last block's hash contains 00 at the start: " + blockchain.last_block.block_hash)