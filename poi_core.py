import hashlib
import time
import random

print("🧠 BARAT Network - Proof of Intelligence (PoI) Core Loading...")

def simulate_scientific_task():
    datasets = ["Cancer_Cell_Data_Chunk_99", "Climate_Model_Grid_402", "Galaxy_Star_Map_77"]
    chosen_task = random.choice(datasets)
    print(f"📥 New Scientific Task Downloaded: {chosen_task}")
    return chosen_task

def mine_poi(task_data):
    print("⚡ Mobile Processing Unit (MPU) Active. Processing scientific data...")
    start_time = time.time()
    target_prefix = "0000"
    nonce = 0
    
    while True:
        data_string = f"{task_data}_{nonce}"
        hash_result = hashlib.sha256(data_string.encode()).hexdigest()
        
        if hash_result.startswith(target_prefix):
            time_taken = time.time() - start_time
            print(f"✅ Task Solved Successfully in {time_taken:.2f} seconds!")
            print(f"🔒 Cryptographic Proof (Hash): {hash_result}")
            print(f"🧠 Reward Awarded: 10 $BARAT Coins credited!")
            break
        nonce += 1

if __name__ == "__main__":
    task = simulate_scientific_task()
    mine_poi(task)
  
