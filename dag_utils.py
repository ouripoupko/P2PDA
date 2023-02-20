def reverse_dag(dag):
    sinks = []
    reverse = {}
    transactions = {}
    for transaction in dag:
        transactions[transaction['hash_code']] = transaction
    for key, transaction in transactions.items():
        for pointer in transaction['content']['functionals']:
            if pointer not in transactions:
                raise Exception('Error: missing transaction')
            if pointer in reverse:
                reverse[pointer].append(key)
            else:
                reverse[pointer] = [key]
        if not transaction['content']['functionals']:
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
