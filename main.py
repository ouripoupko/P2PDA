import sys
import os
import logging
from flask import Flask, request
from flask_cors import CORS
from dag_ds import DagDataStructure

# Create the application instance
app = Flask(__name__, static_folder='static', instance_path=f'{os.getcwd()}/instance')
CORS(app)
logger = app.logger

the_dag = DagDataStructure()

# Create a URL route in our application for human messages
@app.route('/message', methods=['POST'])
def message_handler():
    msg = request.get_json() if request.is_json else None
    logger.info(msg)
    the_dag.create_transaction(msg)
    return {}


# Create a URL route in our application for agents communication
@app.route('/transaction', methods=['POST'])
def transaction_handler():
    msg = request.get_json() if request.is_json else None
    logger.info(msg)
    for transaction in msg:
        the_dag.store_transaction(transaction)
    return {}


# Create a URL route in our application for reading the dag
@app.route('/dag', methods=['GET'])
def dag_handler():
    return [block for block in iter(the_dag)]


# If we're running in stand-alone mode, run the application
if __name__ == '__main__':
    port = int(sys.argv[1])
    conf_kwargs = {'format': '%(asctime)s %(levelname)-8s %(message)s',
                   'datefmt': '%Y-%m-%d %H:%M:%S'}
    logging.basicConfig(**conf_kwargs)

    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=port, use_reloader=False)
