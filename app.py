from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask.logging import create_logger
from sqlalchemy import text
from sqlalchemy.exc import ResourceClosedError
import logging
import os


app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

db_user = os.environ.get('POSTGRES_DB_USER') or 'postgres'
db_psw =  os.environ.get('POSTGRES_DB_PSW') or 'mysecretpassword'
db_host = os.environ.get('SERVICE_POSTGRES_SERVICE_HOST') or 'localhost:5432'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{0}:{1}@{2}'.format(
    db_user, db_psw, db_host
)
db = SQLAlchemy(app)

@app.route("/query", methods=['POST'])
def query():
    """
    Run a query in the db.
    Note that we commit any transaction.
    """

    # Logging the input payload
    json_payload = request.json
    db_query = json_payload['query'] 
    LOG.info(f"Query: \n{db_query}")
    
    sql = text(db_query)
    result = db.engine.execute(sql)

    try:
        json_result = [dict(row) for row in result]
    except ResourceClosedError:
        json_result = 'OK'

    LOG.info(f"Results: \n{result}")

    db.session.commit()

    return jsonify({'result': json_result})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get['PORT'], debug=True)