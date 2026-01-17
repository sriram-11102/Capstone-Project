import csv
import random
import time
import os
from datetime import datetime

class DataGenerator:
    def __init__(self, output_dir="."):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_financial_batch(self, count=100, valid=True):
        """
        Generates a batch of financial records.
        Rules:
        - 1C: TXN... (Alphanum)
        - 2C: Client Name
        - 3C: Currency (USD, EUR, GBP, INR, JPY)
        - 4C: Amount (Numeric > 0)
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        status = "Valid" if valid else "Invalid"
        filename = f"Financial-{status}-{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        currencies = ["USD", "EUR", "GBP", "INR", "JPY"]
        clients = ["Acme Corp", "Globex", "Soylent Corp", "Umbrella Inc", "Stark Ind"]

        print(f"Generating {count} {status} records -> {filename}")

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            for i in range(count):
                # 1. ID
                txn_id = f"TXN{random.randint(10000, 99999)}"
                if not valid and random.random() < 0.1:
                    txn_id = "INVALID_ID" # Fail 'STARTS_WITH TXN'
                
                # 2. Client
                client = random.choice(clients)
                
                # 3. Currency
                currency = random.choice(currencies)
                if not valid and random.random() < 0.1:
                    currency = "BITCOIN" # Fail 'MATCHES (USD|...)'

                # 4. Amount
                amount = round(random.uniform(100.0, 10000.0), 2)
                if not valid and random.random() < 0.1:
                    amount = -50.0 # Fail '> 0'

                writer.writerow([txn_id, client, currency, amount])

        return filepath

if __name__ == "__main__":
    gen = DataGenerator()
    gen.generate_financial_batch(10, True)
    gen.generate_financial_batch(10, False)
