from flask import Flask, jsonify, render_template, request
from flask_cors import CORS, cross_origin
import json
import sys
import csv
import time

sys.path.append("../../")
from Code.prediction_scripts.item_based import recommendForNewUser
from search import Search

import requests

app = Flask(__name__)
app.secret_key = "secret key"
CORS(app, resources={r"/*": {"origins": "*"}})

# Replace 'YOUR_API_KEY' with your actual OMDB API key
OMDB_API_KEY = '26d2e5d0'

def get_movie_info(title):
    index=len(title)-6
    url = f"http://www.omdbapi.com/?t={title[0:index]}&apikey={OMDB_API_KEY}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        res=response.json()
        if(res['Response'] == "True"):
            return res
        else:  
            return { 'Title': title, 'imdbRating':"N/A", 'Genre':'N/A',"Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}
    else:
        return  { 'Title': title, 'imdbRating':"N/A",'Genre':'N/A', "Poster":"https://www.creativefabrica.com/wp-content/uploads/2020/12/29/Line-Corrupted-File-Icon-Office-Graphics-7428407-1.jpg"}

@app.route("/")
def landing_page():
    return render_template("landing_page.html")


@app.route("/predict", methods=["POST"])
# def predict():
#     data = json.loads(request.data)  # contains movies
#     data1 = data["movie_list"]
#     training_data = []
#     for movie in data1:
#         movie_with_rating = {"title": movie, "rating": 5.0}
#         training_data.append(movie_with_rating)
#     recommendations = recommendForNewUser(movie_with_rating)
    
#     for movie in data1:    
#         movie_info = get_movie_info(movie)
#         if movie_info:
#             movie_with_rating["title"]=movie
#             movie_with_rating["rating"]=movie_info["imdbRating"]
    
#     recommendations = recommendations[:10]
#     resp = {"recommendations": recommendations}
#     return resp
def predict():
    data = json.loads(request.data)  # contains movies
    data1 = data["movie_list"]
    training_data = []
    for movie in data1:
        movie_with_rating = {"title": movie, "rating": 5.0}
        training_data.append(movie_with_rating)
    recommendations = recommendForNewUser(training_data)
    recommendations = recommendations[:10]

    for movie in recommendations:
        movie_info = get_movie_info(movie)
        # print(movie_info['imdbRating'])
        if movie_info:
            movie_with_rating[movie+"-r"]=movie_info['imdbRating']
            movie_with_rating[movie+"-g"]=movie_info['Genre']
            movie_with_rating[movie+"-p"]=movie_info['Poster']

    resp = {"recommendations": recommendations, "rating":movie_with_rating}
    return resp

@app.route("/search", methods=["POST"])
def search():
    term = request.form["q"]
    search = Search()
    filtered_dict = search.resultsTop10(term)
    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp

@app.route("/feedback", methods=["POST"])
def feedback():
    data = json.loads(request.data)
    with open(f"experiment_results/feedback_{int(time.time())}.csv", "w") as f:
        for key in data.keys():
            f.write(f"{key} - {data[key]}\n")
    return data

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
