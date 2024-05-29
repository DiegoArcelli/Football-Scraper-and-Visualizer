from flask import Flask
from flask import request, render_template, make_response
from flask_restx import Api, Resource, reqparse
from flask_cors import CORS
from database import DataBase


# def load_html_page(path="./html/page.html"):
#     with open(path, "r") as html_page:
#         text = html_page.read()
#     return text

app = Flask(__name__, template_folder="html")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)
parser = reqparse.RequestParser()

class TeamVisualizationAPI(Resource):

    def get(self):
        headers = {'Content-Type': 'text/html'}
        html_page = render_template("team_page.html")
        return make_response(html_page, 200, headers)

    def self(self):
        headers = {'Content-Type': 'text/html'}
        print(request)
        #html_page = render_template("team_page.html")

class QueryAPI(Resource):

    def post(self):
        data = request.get_json()
        print(data)
        db = DataBase(data)
        return db.execute_query()



if __name__ == "__main__":
    api.add_resource(TeamVisualizationAPI, "/team")
    api.add_resource(QueryAPI, "/query")
    app.run(host='0.0.0.0')