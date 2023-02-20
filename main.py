import sys
import os
from threading import Thread
import logging
from flask import Flask, request
from flask_cors import CORS
from dag_ds import DagDataStructure

# Create the application instance
app = Flask(__name__, static_folder='static', instance_path=f'{os.getcwd()}/instance')
CORS(app)
logger = app.logger

the_dag = DagDataStructure()

def process_transactions(transactions):
    for transaction in transactions:
        the_dag.store_transaction(transaction)

# Create a URL route in our application for human messages
@app.route('/message', methods=['POST'])
def message_handler():
    msg = request.get_json() if request.is_json else None
    logger.info(msg)
    transaction = the_dag.create_transaction(msg)
    return transaction


# Create a URL route in our application for agents communication
@app.route('/transaction', methods=['POST'])
def transaction_handler():
    msg = request.get_json() if request.is_json else None
    logger.info(msg)
    Thread(target=process_transactions, args=(msg,)).start()
    return {}


# Create a URL route in our application for reading the dag
@app.route('/dag', methods=['GET'])
def dag_handler():
    hash_code = request.args.get('hash_code')
    application = request.args.get('application')
    if hash_code:
        return the_dag[hash_code]
    if application:
        return [transaction for transaction in iter(the_dag) if transaction['content']['application'] == application]
    return [transaction for transaction in iter(the_dag)]


# If we're running in stand-alone mode, run the application
if __name__ == '__main__':
    port = int(sys.argv[1])
    conf_kwargs = {'format': '%(asctime)s %(levelname)-8s %(message)s',
                   'datefmt': '%Y-%m-%d %H:%M:%S'}
    logging.basicConfig(**conf_kwargs)

    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=port, use_reloader=False)
