from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
	return "Hello World!"

@app.route('/forward', methods=['POST'])
def forward():
	if(request.form.get('hop_count') > 0):
		return "Will forward to EC2"
	else:
		return "Will forward to destination"

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
