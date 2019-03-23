from flask import Flask
from flask import request
import time


app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello():
    print("->", request.form)
    data = request.args
    origin_ts = data['timestamp']
    # need to convert to sec
    time_elapsed = time.time()-float(origin_ts)
    return ("time taken for request: " str(time_elapsed))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run(host="0.0.0.0",port=8000)