import datetime
import uuid
from random import randint

import pymongo
from flask import Flask
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('mongodb://localhost:27017/',
                     username='root',
                     password='example')
db = client.test_database

app = Flask(__name__)


@app.route('/create_stocks/')
def create_stocks():
    stocks = db.stocks
    stocks.drop()
    stocks.insert_many([{
        'sku': 'sku-1',
        'qty': 1000
    }, {
        'sku': 'sku-2',
        'qty': 50
    }, {
        'sku': 'sku-3',
        'qty': 50
    }, {
        'sku': 'sku-4',
        'qty': 50
    }, {
        'sku': 'sku-5',
        'qty': 50
    }])
    stocks.create_index('sku', unique=True)

    reserves = db.reserves
    reserves.drop()
    db.create_collection('reserves')
    reserves = db.reserves
    reserves.create_index('sku')
    reserves.create_index([('sku', pymongo.ASCENDING), ('status', pymongo.ASCENDING)])
    reserves.create_index('batch')

    return {'message': 'ok'}


@app.route('/report/')
def report():
    ret = db.reserves.aggregate([{
        '$group': {
            '_id': ['$sku', '$status'],
            'total': {'$sum': '$qty'}
        }
    }])
    return dumps(ret)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@app.route('/load/')
def load():
    for _ in range(0, 1000):
        chunk = []
        batch = uuid.uuid4()
        for _ in range(0, 1000):
            sku = randint(1, 5)
            chunk.append({
                'sku': f'sku-{sku}',
                'qty': randint(1, 10),
                'status': 'fail' if sku == 1 else ['ok', 'pre', 'fail'][randint(0, 2)],
                'batch': batch
            })
        db.reserves.insert_many(chunk)

    return 'ok'


@app.route('/reserves/<sku>/')
def reserve(sku):
    qty = randint(1, 10)
    batch = uuid.uuid4()
    reserves = db.reserves
    stocks = db.stocks
    reserves.insert_one({
        'sku': sku,
        'qty': qty,
        'status': 'pre',
        'batch': batch
    })

    stock = stocks.find_one({'sku': sku})
    total_reserve = reserves.aggregate([{
        '$match': {
            'sku': sku,
            'status': {'$in': ['ok', 'pre']}
        },
    }, {
        '$group': {
            '_id': '$sku',
            'total': {'$sum': '$qty'}
        }
    }]).next()

    available = stock.get('qty', 0) - total_reserve.get('total', 0)
    if available >= 0:
        reserves.update_many({'batch': batch}, {'$set': {'status': 'ok'}})
        return dumps(['ok', sku, qty, available, stock, total_reserve])

    reserves.delete_many({'batch': batch})
    # reserves.update_many({'batch': batch}, {'$set': {'status': 'fail'}})
    return dumps(['fail', sku, qty, available, stock, total_reserve])


