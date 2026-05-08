import random
#import matplotlib.pyplot as plt
import numpy as np
import csv
from collections import Counter


def adjust_top_item_frequencies(transactional_data, top_items, min_diff, max_diff):
    adjusted_transactions = transactional_data.copy()

    all_items = [item for transaction in adjusted_transactions for item in transaction]
    item_counts = Counter(all_items)

    for item, current_count in top_items:
        random_adjustment = random.randint(min_diff, max_diff) * random.choice([-1, 1])
        target_count = max(0, current_count + random_adjustment)

        if target_count > current_count:
            for _ in range(target_count - current_count):
                random_transaction = random.choice(adjusted_transactions)
                random_transaction.append(item)
                
        elif target_count < current_count:
            remove_count = current_count - target_count
            for _ in range(remove_count):
                for transaction in adjusted_transactions:
                    if item in transaction:
                        transaction.remove(item)
                        break

    return adjusted_transactions

def encode(response, domain):
    return [1 if d == response else 0 for d in domain]

def gen_size_distribution(peak_size, max_transaction_size, jitter_strenght):
    sizes = list(range(1, max_transaction_size + 1))

    delay = 6
    peak = 2
    ratio = 1.5
    
    weights = []
    
    for size in sizes:
        if size < peak_size:
            weight = ((size/1.5) / peak_size) ** 2

        elif size == peak_size:
            weight = peak

        elif peak_size < size < peak_size + delay:
            weight = peak / ((((size - 1) / peak_size) ** 2)) + random.uniform(-jitter_strenght * 0.5, jitter_strenght * 1.2)
        
        elif size > max_transaction_size - max_transaction_size / 10:
            weight = random.uniform(0, jitter_strenght * 2)
        
        else:
            weight = peak / ((((size - 1) / peak_size) ** 2)) + random.uniform(-jitter_strenght * 0.5, jitter_strenght * 1.2)
            #weight = peak / (ratio * size)
        
        jitter = random.uniform(-jitter_strenght, jitter_strenght)
        weight += jitter
        
        weight = max(weight, 0)
        weights.append(weight)
    
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    return normalized_weights

def gen_transactional_data(peak_size, n, d, max_transaction_size, jitter_strenght):
    size_distribution = gen_size_distribution(peak_size, max_transaction_size, jitter_strenght)
    
    transactional_data = []
    
    super_common_items = [3]  # Super common item
    common_items = random.sample(range(2, 23), 10)  # 10 random items
    less_common_items = random.sample(range(10, 100), 40)  # 40 random items
    uncommon_items = random.sample(range(100, 501), 100)  # 100 random items

    common_weights = [random.uniform(0.8, 1.2) for _ in common_items]
    less_common_weights = [random.uniform(0.5, 1.5) for _ in less_common_items]
    uncommon_weights = [random.uniform(0.3, 1.7) for _ in uncommon_items]

    total_common_weight = sum(common_weights)
    common_weights = [w / total_common_weight for w in common_weights]

    total_less_common_weight = sum(less_common_weights)
    less_common_weights = [w / total_less_common_weight for w in less_common_weights]

    total_uncommon_weight = sum(uncommon_weights)
    uncommon_weights = [w / total_uncommon_weight for w in uncommon_weights]
    
    for _ in range(n):
        num_items = min(
            random.choices(range(1, max_transaction_size + 1), weights=size_distribution, k=1)[0],
            max_transaction_size
        )

        transaction = set()
        
        while len(transaction) < num_items:
            rand = random.random()
            if rand < 0.6:
                transaction.add(random.choice(super_common_items))
            elif rand < 0.7:
                transaction.add(random.choices(common_items, weights=common_weights, k=1)[0])
            elif rand < 0.8:
                transaction.add(random.choices(less_common_items, weights=less_common_weights, k=1)[0])
            elif rand < 0.9:
                transaction.add(random.choices(uncommon_items, weights=uncommon_weights, k=1)[0])
            else:
                transaction.add(random.randint(501, d))
        transactional_data.append(list(transaction))
    
    return transactional_data

n = 515596  # Number of users
d = 1657  # Total domain size
max_transaction_size = 164  # Maximum number of items per transaction
peak_size = 8  # The size at which the distribution spikes
jitter_strength = 0.01  # Strength of the jitter to add variability

transactional_data = gen_transactional_data(peak_size, n, d, max_transaction_size, jitter_strength)

""" # Generate and plot the size distribution
size_distribution = gen_size_distribution(peak_size, max_transaction_size, jitter_strength)
#print(size_distribution)
plt.figure(figsize=(10, 6))
plt.bar(range(1, max_transaction_size + 1), size_distribution)
plt.xlabel('Transaction Size')
plt.ylabel('Probability')
plt.title('Transaction Size Probability Distribution')
plt.show()
 """

transaction_sizes = [len(transaction) for transaction in transactional_data]

output_file = "Data/Shark_fin.csv"
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for transaction in transactional_data:
        writer.writerow(transaction)

#print(f"Transactional data saved to {output_file}")

domain_t = list(range(1, max_transaction_size+1))
#print("d: ", max_transaction_size)
#print("domain: ", domain_t)
r = np.zeros(max_transaction_size)
#print(transaction_sizes)

for transaction_size in transaction_sizes:
    r += encode(transaction_size, domain_t)
r = r.astype(int)
#print(r)

""" # Plot histogram of transaction sizes
plt.figure(figsize=(10, 6))
plt.bar(range(1, max_transaction_size+1), r)
plt.xlabel('Transaction Size')
plt.ylabel('Number of Users')
plt.title('Histogram of Transaction Sizes')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()  """

""" # Find the top 10 items in the transactional data
item_counter = Counter(item for transaction in transactional_data for item in transaction)
top_10_items = item_counter.most_common(64)
print("Top 10 items:")
for item, count in top_10_items:
    print(f"Item {item}: {count} occurrences")


 """
##########adjust to counts

item_counter = Counter(item for transaction in transactional_data for item in transaction)
top_64_items = item_counter.most_common(64)

min_diff = 500
max_diff = 3500
adjusted_data = adjust_top_item_frequencies(transactional_data, top_64_items, min_diff, max_diff)

adjusted_item_counter = Counter(item for transaction in adjusted_data for item in transaction)
adjusted_top_64_items = adjusted_item_counter.most_common(64)

""" # Print adjusted top 64 items
print("\nAdjusted Top 64 items:")
for item, count in adjusted_top_64_items:
    print(f"Item {item}: {count} occurrences")
 """

adjusted_output_file = "Data/Shark_fin.csv"
with open(adjusted_output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for transaction in adjusted_data:
        writer.writerow(transaction)

""" print(f"Adjusted transactional data saved to {adjusted_output_file}")

adjusted_transaction_sizes = [len(transaction) for transaction in adjusted_data]

# Count the frequency of each transaction size
size_counts = Counter(adjusted_transaction_sizes)

# Plot histogram of adjusted transaction sizes
plt.figure(figsize=(10, 6))
plt.bar(size_counts.keys(), size_counts.values())
plt.xlabel('Transaction Size')
plt.ylabel('Number of Users')
plt.title('Histogram of Adjusted Transaction Sizes')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show() """