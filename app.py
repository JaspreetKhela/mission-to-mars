# _____

# Import dependencies
# _____

# Import and use Flask to render a template, redirecting to another url, and creating a URL
from flask import Flask, render_template, redirect, url_for

# Import and use PyMongo to interact with our Mongo database
from flask_pymongo import PyMongo

# Import and use the scraping code in scraping.py
import scraping

# _____

# Flask app
# _____

# Create an instance of the Flask app
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# _____

# App routes
# _____

# Define the route for the homepage
@app.route("/")
def index():
    # Ask PyMongo to find the "mars" collection in our database
   mars = mongo.db.mars.find_one()

   # Tell Flask to return an HTML template using an index.html file in the root directory
   return render_template("index.html", mars=mars)

# Define the route for the web scrape, which then returns back to the homepage with the scraped content
@app.route("/scrape")
def scrape():
    # Assign a new variable that points to our Mongo database
   mars = mongo.db.mars

   # Store the newly scraped data; the scrape_all() function is defined in the scraping.py code
   mars_data = scraping.scrape_all()

   # Update the database
   # The first parameter - the query paramenter - updates the first matching document in the collection (since we used {} instead of specifying a field to update)
   # The second parameter modifies the document using the mars_data
   # The third parameter indicates to Mongo to create a new document if one doesn't already exist, and new data will always be saved (even if we haven't already created a document for it)
   mars.update_one({}, {"$set":mars_data}, upsert=True)

   # Navigate back to the homepage with the updated content
   return redirect('/', code=302)

# Define the route for the images
@app.route("/mars_hemispheres")
def mars_hemispheres():
    # Ask PyMongo to find the "mars" collection in our database
    mars = mongo.db.mars.find_one()

    return render_template("hemispheres.html", mars=mars)

if __name__ == "__main__":
   app.run()
