from flask import Flask
from flask import request
import time
# import signal
# import sys
import atexit

app = Flask(__name__)

routingTimes = []

def exit_handler():
        print('exit_handler called')
        print("length of routingTimes:", len(routingTimes))
        with open('times.txt', 'a+') as f:
            for time_elapsed in routingTimes:
                f.write(time_elapsed + "\n")
        sys.exit(0)

@app.route('/', methods=['GET','POST'])
def hello():
    # print("->", request.form)
    receivedTime = time.time()
    data = request.args
    origin_ts = data['timestamp']
    # need to convert to sec
    time_elapsed = str(receivedTime-float(origin_ts))
    routingTimes.append(time_elapsed)

    # print(str(time_elapsed))
    return ("time taken for request: " + str(time_elapsed))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # signal.signal(signal.SIGINT, signal_handler)
    # print('Press Ctrl+C to exit')
    atexit.register(exit_handler)
    app.debug = True
    app.run(host="0.0.0.0",port=8000)
    # signal.pause()

