from flask import Flask
from flask import request, render_template, make_response
from flask_restx import Api, Resource, reqparse
from flask_cors import CORS
from database import DataBase
from utils import *


# # def load_html_page(path="./html/page.html"):
# #     with open(path, "r") as html_page:
# #         text = html_page.read()
# #     return text

# app = Flask(__name__, template_folder="html")
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

# api = Api(app)
# parser = reqparse.RequestParser()

# class TeamVisualizationAPI(Resource):

#     def get(self):
#         headers = {'Content-Type': 'text/html'}
#         html_page = render_template("team_page.html")
#         return make_response(html_page, 200, headers)

#     def self(self):
#         headers = {'Content-Type': 'text/html'}
#         print(request)
#         #html_page = render_template("team_page.html")



# @app.route('/read-form', methods=['POST']) 
# class QueryAPI(Resource):

#     def post(self):

#         print(data)

#         # data = request.get_json()
#         # print(data)

#         # db = DataBase(data)
#         # plot_html_code =  db.execute_query()
#         # page_html_code = add_code("./html/team_page.html", plot_html_code)
#         # print(page_html_code)

#         # headers = {'Content-Type': 'text/html'}
#         # html_page = render_template("team_page.html")
#         # return make_response(html_page, 200, headers)

#         # return plot_html_code


app = Flask(__name__, template_folder="html")
  



# @app.route('/team', methods=['GET']) 
# def index(): 
#     ## Display the HTML form template  
#     return render_template('team_page.html') 
  
# `read-form` endpoint  
@app.route('/team', methods=['GET', 'POST']) 
def read_form():

    if request.method == "GET":
        plot_html_code = ""
    elif request.method == "POST":
        data = request.form
        dict_data = {}
        print(data.keys())
        for key in data.keys():
            if key != "leagues":
                dict_data[key] = data[key]
            else:
                dict_data[key] = data.getlist(key)

        print(dict_data)

        dict_data["x_label"] = dict_data["x_axis"] if dict_data["x_label"] == "" else dict_data["x_label"]
        dict_data["y_label"] = dict_data["y_axis"] if dict_data["y_label"] == "" else dict_data["y_label"]            
        dict_data["title"] = f"{dict_data['x_label']} vs {dict_data['y_label']}" if dict_data["title"] == "" else dict_data["title"]


        print(dict_data)

        db = DataBase(dict_data)
        plot_html_code =  db.execute_query()
        return plot_html_code
        page_html_code = add_code("./html/team_page.html", plot_html_code)

        return page_html_code
    # print(page_html_code[:100])
    return render_template('team_page.html', plot_code=plot_html_code) 

    


if __name__ == "__main__":
    # api.add_resource(TeamVisualizationAPI, "/team")
    # api.add_resource(QueryAPI, "/query")
    app.run(host='0.0.0.0')