Flask Development Setup
=======================

1) Install Python3, run `sudo apt-get update`
2) Create new project dir: `mkdir project-dir`
3) Enter project dir: `cd project-dir`
4) Download the repo, set environment, and install dependencies: `git clone https://github.com/mmahmad/cs538-project.git && sudo apt-get install python3-venv -y && python3 -m venv venv && source venv/bin/activate && cd cs538-project && pip install -r requirements.txt`
5) Start the server: `python run app.py <location>`. Locations are `ohio`, `nvirg`, `ncali`. (server reachable on 0.0.0.0, configurable from `app.run()` in `main()`.