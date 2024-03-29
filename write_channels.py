"""This service allows to write new channels to db"""
import os
import sys
import time
import MySQLdb
from rq import Worker, Queue, Connection
from methods.connection import get_redis, get_cursor

r = get_redis()

def write_channels(data):
    """Write channels into database (table channels)
       data must be a 2d array - [n][12]"""
    cursor, db = get_cursor()
    if not cursor or not db:
        # log that failed getting cursor
        return False
    try:
        for chan in data:
            if chan is None or len(chan) != 12:
                return False
        q = '''REPLACE INTO channels
                (id, title, description, custom_url,
                published_at, default_language, views,
                subscribers, hidden_subscribers, videos,
                keywords, country)
                VALUES
                (%s, %s, %s, %s, %s, %s,
                 %s, %s, %s, %s, %s, %s);'''
        cursor.executemany(q, data)
    except Exception as error:
        print(error)
        # LOG
        return False
        # sys.exit("Error:Failed writing new chanles to db")
    db.commit()
    return True


if __name__ == '__main__':
    q = Queue('write_channels', connection=r)
    with Connection(r):
        worker = Worker([q], connection=r,  name='write_channels')
        worker.work()
