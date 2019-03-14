Development Setup
=================

1) Install Python3
2) Create new project dir: `mkdir project-dir`
3) Enter project dir: `cd project-dir`
4) Create virtual environment: `python3 -m venv venv`
5) Activate virtual environment: `source venv/bin/activate`
6) Clone project: `git clone https://github.com/mmahmad/cs538-project.git`
7) Change dir to project: `cd cs538-project`
8) Install Flask and dependencies: `pip install -r requirements.txt`
9) Export FLASK_APP variable: `export FLASK_APP=path/to/app.py` (you can add this to your shell profile settings in ~/.bash_profile) 
10) Run server: `flask run --host=0.0.0.0` (default port is 5000)