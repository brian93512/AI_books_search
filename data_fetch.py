import json
import redis
import requests
import threading
import time

EPOCH_INTERVAL_SEC = 4
MAX_N = 50
REDIS_PORT = 6379
DATA_LAST_TIME_IN_REDIS_SEC = EPOCH_INTERVAL_SEC * MAX_N
URL = "https://di37ol03g7.execute-api.us-west-2.amazonaws.com/dev/"

def fetch():
    """
    fetch book data into redis in every epoch
    """
    threading.Timer(EPOCH_INTERVAL_SEC, fetch).start()
    now = str(int(time.time()))
    response = requests.post(URL)
    html = json.loads(response.text)
    res = html['results']
    res.sort(key=lambda x: -x["review_score"])
    dic = json.dumps(res)
    p = r.pipeline()
    p.set(now, dic)
    p.expire(now, DATA_LAST_TIME_IN_REDIS_SEC)
    p.execute()
    # print "insert :", now

if __name__ == '__main__':
    r = redis.StrictRedis(host='localhost', port=REDIS_PORT, db=0)
    fetch()
