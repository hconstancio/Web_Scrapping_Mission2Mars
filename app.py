# Import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape

# Initiate Flask app
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars"

# Use flask_pymongo to set up mongo connection
mongo = PyMongo(app)

@app.route("/")
def home():

    # Find data
    mars = mongo.db.mars.find_one()
    print("home: ", mars)
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def data_scrape():
    mars = mongo.db.mars
    mars_data = scrape.scrape()
    print("mars_data: ", mars_data)
    mars.update(
        {}, 
        mars_data, 
        upsert=True
        )
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)