import uuid
from json import dumps
from random import randint
import pandas as pd

from flask import Flask
from flask_mysql_connector import MySQL


app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE'] = 'test_database'
app.config['MYSQL_AUTOCOMMIT'] = True

mysql = MySQL(app)


def _execute_sql(cursor, sql, params, to_pandas=False):
    cursor.execute(sql, params)
    if to_pandas:
        out = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
    else:
        out = cursor.fetchall()
    return out


@app.route('/create_stocks/')
def create_stocks():
    cnx = mysql.connection
    cur = mysql.new_cursor(dictionary=True)
    cur.execute('TRUNCATE TABLE stocks')
    cur.execute('TRUNCATE TABLE reserves')
    cur.execute(
        "INSERT INTO stocks(sku, qty) values ('sku-1', 1000), ('sku-2', 50), ('sku-3', 50), ('sku-4', 50), ('sku-5', 50)")
    # cnx.commit()
    cur.close()

    return {'message': 'ok'}


@app.route('/report/')
def report():
    ret = mysql.execute_sql(
        'SELECT sku, status, CAST(sum(qty) as SIGNED) as total from reserves GROUP BY sku, status',
        to_pandas=False)
    return dumps(ret)


@app.route('/reserves/<sku>/')
def reserve(sku):
    qty = randint(1, 10)
    batch = str(uuid.uuid4())

    cur = mysql.new_cursor(dictionary=True)
    # cur.execute('SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
    cur.execute("INSERT INTO reserves(sku, qty, batch, status) VALUES(%(sku)s, %(qty)s, %(batch)s, %(status)s)", {
        'sku': sku,
        'qty': qty,
        'status': 'pre',
        'batch': batch
    })
    stock = _execute_sql(cur, 'SELECT * FROM stocks WHERE sku = %(sku)s', {'sku': sku}, to_pandas=False)[0]
    total_reserve = _execute_sql(
        cur,
        "SELECT sku, SUM(qty) as total FROM reserves WHERE sku = %(sku)s AND status IN ('pre', 'ok')",
        {'sku': sku},
    )[0]
    available = stock.get('qty', 0) - total_reserve.get('total', 0)

    if available >= 0:
        cur.execute("UPDATE reserves SET status = 'ok' WHERE batch = %(batch)s", {'batch': batch})
        # mysql.connection.commit()
        cur.close()
        return 'ok'
    # mysql.connection.rollback()
    cur.execute("UPDATE reserves SET status = 'fail' WHERE batch = %(batch)s", {'batch': batch})
    cur.close()
    return 'fail'


@app.route('/load/')
def load():
    for _ in range(0, 1000):
        chunk = []
        batch = str(uuid.uuid4())
        for _ in range(0, 1000):
            sku = randint(1, 5)
            chunk.append(
                (f'sku-{sku}', randint(1, 10), 'fail' if sku == 1 else ['ok', 'pre', 'fail'][randint(0, 2)], batch))

        cur = mysql.new_cursor(dictionary=True)
        cur.executemany("INSERT INTO reserves(sku, qty, status, batch) values (%s, %s, %s, %s)", chunk)
        mysql.connection.commit()

    return 'ok'
