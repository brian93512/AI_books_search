# AI_books_search
this is a web service to find top review books and their key words from The-Book website

## How It Works
Epoch: a epoch is defined by a api call, every 4 seconds
N is a counter on epochs, where N=1 is the epoch (currentTime, currentTime - 4secs), N = 10 is the epoch (currentTime - 36secs, currentTime - 40secs)

1. top review: enter the epoch time from now N (1~50) and number of top books X (1~50), it will return top X books with their review scores
   api: http://ec2-18-188-8-28.us-east-2.compute.amazonaws.com:5002/topReview/<N>/<X>

2. top similarity: enter the epoch time from now N (1~50) and number of top books X (1~50), it will return top X books and the similarity score among other top review books
   api: http://ec2-18-188-8-28.us-east-2.compute.amazonaws.com:5002/topSimilarity/<N>/<X>
   
3. top key words: enter the epoch time from now N (1~50) and number of top books X (1~50), it will return top X books with their top 5 key words
   api: http://ec2-18-188-8-28.us-east-2.compute.amazonaws.com:5002/topKeyWords/<N>/<X>