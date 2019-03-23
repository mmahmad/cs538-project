from flask import Flask
from flask import request
import time


app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def hello():
    print("->", request.form)
    data = request.form
    origin_ts = data['timestamp']
    # need to convert to sec
    time_elapsed = time.time()-float(origin_ts)
    return str("time taken for request: ", time_elapsed)


# run the app.
if _name_ == "_main_":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run(host="localhost",port=8000)