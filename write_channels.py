"""This service allows to write new channels to db"""
import os
import sys
import time
import MySQLdb
from rq import Worker, Queue, Connection
from methods.connection import get_redis, get_cursor


def write_channels(data):
    """Write channels into database (table channels)
       data must be a 2d array - [n][12]"""
    cursor, db = get_cursor()
    for chan in data:
        if len(chan) != 12:
            return False
    q = '''INSERT INTO  channels
            (id, title, description, custom_url,
            published_at, default_language, views,
            subscribers, hidden_subscribers, videos,
            keywords, country)
            VALUES
            (%s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, );'''
    try:
        cursor.executemany(q, data)
    except MySQLdb.Error as error:
        print(error)
        sys.exit("Error:Failed writing new chanles to db")
    cursor.execute()
    db.commit()
    return True


if __name__ == '__main__':
    time.sleep(5)
    r = get_redis()
    q = Queue('write_channels', connection=r)
    with Connection(r):
        worker = Worker([q], connection=r,  name='write_channels')
        worker.work()
