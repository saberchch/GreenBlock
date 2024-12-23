import json
import os
from datetime import datetime
from app.block import Block
from app.transaction import Transaction
from app.DID import DID
from app.balance import BalanceManager
from flask import flash
from app.secret import SecretManager

class Blockchain:
    def __init__(self, filename='blockchain.json'):
        self.chain = []
        self.current_transactions = []  # List to hold current transactions
        self.filename = filename
        self.balance_manager = BalanceManager()  # Initialize balance manager
        self.secret_manager = SecretManager()  # Create an instance of SecretManager
        self.load_blockchain()
    
    def create_genesis_block(self):
        """Create the genesis block and add it to the blockchain."""
        genesis_block = Block(0, [], "0", nonce=0)
        self.chain.append(genesis_block)
        self.save_blockchain()
        print("Genesis block created.")

    def save_blockchain(self):
        """Save the blockchain to a file."""
        with open(self.filename, 'w') as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)
        print(f"Blockchain saved to {self.filename}.")  # Debugging output

    def load_blockchain(self):
        """Load the blockchain from a file, or create a genesis block if the file is empty or missing."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    chain_data = json.load(f)
                    if chain_data:
                        self.chain = [Block.from_dict(block_data) for block_data in chain_data]
                        print(f"Blockchain loaded from {self.filename}.")
                    else:
                        print("Blockchain file is empty. Initializing with a genesis block.")
                        self.create_genesis_block()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading blockchain: {e}. Initializing with a genesis block.")
                self.create_genesis_block()
        else:
            print("Blockchain file not found. Initializing with a genesis block.")
            self.create_genesis_block()

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

    def add_user(self, username, secret_phrase, profession):
        """Add a new user to the blockchain as a user registration transaction."""
        # Check if the user already exists
        if self.get_user_data(username):
            raise ValueError("User already exists.")

        # Generate a public key from the secret phrase
        public_key_pem, _ = self.secret_manager.generate_key_from_secret_phrase(secret_phrase)

        # Encrypt the secret phrase for storage
        encrypted_secret = self.secret_manager.encrypt_secret_phrase(secret_phrase)

        # Create the user registration transaction
        transaction_data = {
            "encrypted_secret_phrase": encrypted_secret,
            "public_key": public_key_pem.decode(),  # Ensure it's a string
            "profession": profession
        }

        transaction = {
            "operation": "USER_REGISTRATION",
            "sender": username,
            "recipient": "SYSTEM",
            "data": transaction_data,
            "timestamp": datetime.now().timestamp(),
            "state": "Processed",
            "hash": "",  # Placeholder for the hash
        }

        # Calculate the hash for the transaction here
        transaction["hash"] = self.calculate_hash(transaction)  # Implement this method

        # Add the transaction to the current transactions
        self.current_transactions.append(transaction)

        # Add the block with the user registration transaction
        new_block = self.add_block()  # Ensure this is called to add the transaction to the blockchain

        print(f"New block added: {new_block}")  # Debugging output
        return True, "Registration successful!"

    def get_user_data(self, username):
        """Retrieve user-specific data from the blockchain."""
        for user in self.chain:
            if user['username'] == username:
                return user
        return None

    def add_contribution(self, contribution):
        """Add a contribution to the blockchain."""
        self.current_transactions.append(contribution)
        self.save_blockchain()

    def get_user_contributions(self, username):
        """Retrieve all contributions for a specific user."""
        return [contribution for contribution in self.current_transactions if contribution['user'] == username]
        
    def add_transaction(self, sender, recipient, operation, data):
        """Add a new transaction to the list of current transactions."""
        transaction = Transaction(
            operation=operation,
            sender=sender,
            recipient=recipient,
            data=data
        )
        self.current_transactions.append(transaction)
        return transaction

    def add_block(self):
        """Add a new block to the blockchain."""
        previous_hash = self.last_block.hash if self.last_block else "0"
        new_block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.now().timestamp(),
            "transactions": self.current_transactions,
            "previous_hash": previous_hash,
            "nonce": str(datetime.now()),  # You may want to implement a proper nonce calculation
            "hash": "",  # Placeholder for the hash
        }

        # Calculate the hash for the new block here
        new_block["hash"] = self.calculate_hash(new_block)  # Implement this method

        self.chain.append(new_block)
        self.current_transactions = []  # Reset the current transactions
        self.save_blockchain()  # Save the updated blockchain to the file
        return new_block

    def validate_chain(self):
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if the current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid hash in block {i}")
                return False

            # Check if the previous_hash field points to the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash in block {i}")
                return False

        return True

    def is_username_available(self, username):
        """Check if a username is available for registration."""
        for user in self.chain:
            if user['username'] == username:
                return False
        return True

    def find_did_in_blockchain(self, user_identifier):
        """Search for a DID in the blockchain."""
        for index, block in enumerate(self.chain):
            for transaction in block.transactions:
                if transaction.sender == user_identifier and transaction.operation == "STORE_DID":
                    return json.loads(transaction.data)  # Return the parsed JSON object
        return None

    def validate_transaction(self, transaction):
        """Validate a transaction before adding it to the blockchain."""
        # Implement validation logic (e.g., check signatures, ensure sender has sufficient balance)
        return True  # Placeholder for actual validation logic

    def get_user_transactions(self, username):
        """Retrieve all transactions for a specific user."""
        user_transactions = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == username or transaction.recipient == username:
                    user_transactions.append(transaction)
        return user_transactions

    def add_project(self, project):
        """Add a new project to the blockchain."""
        self.current_transactions.append(project)
        self.save_blockchain()
