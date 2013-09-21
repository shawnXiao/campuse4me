from flask import Flask
from flask import request
from searchEngin import JobHunterEngin
app = Flask(__name__)

@app.route("/")
def index_page():
    return "Hello! campuse4me welcome to you!"
@app.route("/getJobInfo")
def getJobInfo():
    keyword = request.args.get("keyword")
    city = request.args.get("city")
    jobSearcEngin = JobHunterEngin(keyword, city)
    jobSearcEngin.initBr()
    return jobSearcEngin.fetch()

if __name__ == '__main__':
    app.run()


