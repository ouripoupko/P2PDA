def find_sources(dag):
    sources = {}
    transactions = {}
    for transaction in dag:
        sources[transaction['hash_code']] = transaction
        transactions[transaction['hash_code']] = transaction
    for transaction in dag:
        for key in transaction['content']['functionals']:
            if key in sources:
                sources.pop(key)
    return sources, transactions

def order_sources(sources, transactions):
    index = {}
    counter = 0
    current = sources
    while current:
        next_sources = []
        for key in current:
            index[key] = counter
            next_sources.extend([child
                                 for child in transactions[key]['content']['functionals']
                                 if child in transactions])
        current = next_sources
        counter += 1
    order = [[] for i in range(counter)]
    for key in index:
        order[counter-index[key]-1].append(key)
    return order
