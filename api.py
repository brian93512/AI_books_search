from flask import Flask, request
from flask_restful import Resource, Api
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import redis
import time

STOP_WORDS = set(stopwords.words('english'))
NUM_TOP_KEY_WORDS = 5
EPOCH_INTERVAL_SEC = 4
REDIS_PORT = 6379
FLASK_PORT = '5002'

def _search(N, curr_time):
    """
    get books in time interval N from current time
    :type N: str
    :type curr_time: int
    :rtype: dict
    """
    res = []
    for key in xrange(curr_time - N * EPOCH_INTERVAL_SEC, curr_time - (N - 1) * EPOCH_INTERVAL_SEC):
        if str(key) in r:
            books = r.get(str(key))
            res = json.loads(books)
    return res


def _normalize_text(s):
    """
    do stemming and remove stop words in s
    :type s: str
    :rtype: str 
    """
    # word stemming
    s = [SnowballStemmer("english").stem(word) for word in s.split(" ")]

    # remove stop words
    s = [word for word in s if not word in STOP_WORDS]
    s = " ".join(s)
    return s


def _getKeyWordsPairs(titles, summaries):
    """
    use tf-idf to find key words in summaries
    :type titles: list
    :type summaries: list
    :rtype: dict
    """
    documents = [_normalize_text(summary) for summary in summaries]
    vectorizer = CountVectorizer()
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(
        vectorizer.fit_transform(documents))
    words = vectorizer.get_feature_names()
    weights = tfidf.toarray()
    res = []
    for i in xrange(len(weights)):
        top_words = []
        for j in xrange(len(words)):
            top_words.append((weights[i][j], words[j]))
        top_words.sort(reverse=True)
        res.append({titles[i]: [pair[1] for pair in
                                top_words[:NUM_TOP_KEY_WORDS]]})
    return res


def _isInvalidInput(N, X):
    """
    check if input N and X is valid 
    :type N: str
    :type X: str
    :rtype: str or None
    """
    if not N.isdigit() or not X.isdigit():
        return "Time interval and top number of books should be integer only"
    N, X = int(N), int(X)
    if (N < 1 or N > 50) or (X < 1 or X > 50):
        return ("Time Interval should be within 1 and 50. " 
        "Top number of books should be within 1 and 50.")


class TopReview(Resource):
    """A Class to handle request for top reivew"""

    def get(self, N, X):
        """
        get X top review books in time interval N from now
        :type N: str
        :type X: str
        :rtype: dict
        """
        if _isInvalidInput(N, X):
            return {"Invalid Input": _isInvalidInput(N, X)}
        N, X = int(N), int(X)
        curr_time = int(time.time())
        books = _search(N, curr_time)
        if books:
            top_x = books[:X]
            top_X_titles = [{x["title"]: x["review_score"]} for x in top_x]
            return top_X_titles
        else:
            return {"No books Found!": "No books Found!"}


class TopSimilarity(Resource):
    """A Class to handle request for top similarity books"""

    def get(self, N, X):
        """
        get X top review books and their similarity between each 
        other top book in time interval N from now 
        :type N: str
        :type X: str
        :rtype: dict
        """
        if _isInvalidInput(N, X):
            return {"Invalid Input": _isInvalidInput(N, X)}
        N, X = int(N), int(X)
        curr_time = int(time.time())
        books = _search(N, curr_time)
        if books:
            top_x = books[:X]
            titles = [x["title"] for x in top_x]
            tfidf = TfidfVectorizer().fit_transform(titles)
            pairwise_sim = tfidf * tfidf.T
            res = []
            for i, title in enumerate(titles):
                score_pairs = []
                for j in xrange(len(titles)):
                    if i != j:
                        sim = {"title": titles[j], "similarity": str(
                            int(round(pairwise_sim.A[i][j], 2) * 100))}
                        score_pairs.append(sim)
                res.append({title: score_pairs})
            return res
        else:
            return {"error": "No books Found!"}


class TopKeyWords(Resource):
    """A Class to handle top key words request"""

    def get(self, N, X):
        """
        get X top review books and their key words in time interval N from now 
        :type N: str
        :type X: str
        :rtype: dict
        """
        if _isInvalidInput(N, X):
            return {"Invalid Input": _isInvalidInput(N, X)}
        N, X = int(N), int(X)
        curr_time = int(time.time())
        books = _search(N, curr_time)
        if books:
            top_x = books[:X]
            titles = [x["title"] for x in top_x]
            summaries = [x["summary"] for x in top_x]
            keyword_pairs = _getKeyWordsPairs(titles, summaries)
            return keyword_pairs
        else:
            return {"error": "No books Found!"}


if __name__ == '__main__':
    r = redis.StrictRedis(host='localhost', port=REDIS_PORT, db=0)
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(TopReview, '/topReview/<N>/<X>')
    api.add_resource(TopSimilarity, '/topSimilarity/<N>/<X>')
    api.add_resource(TopKeyWords, '/topKeyWords/<N>/<X>')
    app.run(host='0.0.0.0', port=FLASK_PORT)
