def reverse_dag(dag):
    sinks = []
    reverse = {}
    transactions = {}
    for transaction in dag:
        transactions[transaction['hash_code']] = transaction
    for key, transaction in transactions.items():
        is_sink = True
        for pointer in transaction['pointers']:
            if pointer in transactions:
                is_sink = False
                if pointer in reverse:
                    reverse[pointer].append(key)
                else:
                    reverse[pointer] = [key]
        if is_sink:
            sinks.append(key)
    return sinks, reverse, transactions

def order_dag(sinks, pointers):
    index = {}
    counter = 0
    current = sinks
    while current:
        next_sinks = []
        for key in current:
            index[key] = counter
            if key in pointers:
                next_sinks.extend(pointers[key])
        current = next_sinks
        counter += 1
    order = [[] for i in range(counter)]
    for key in index:
        order[index[key]].append(key)
    return order
