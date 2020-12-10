# import necessary libraries
import os
import numpy as np
import listings as dp

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

from flask_sqlalchemy import SQLAlchemy

# Postgres database user and password import
from db_key import user, password

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################
try:
    db_uri = os.environ['DATABASE_URL']
except KeyError:
    db_uri = f'postgres://{user}:pip@localhost:5432/airbnb_db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

#################################################
# Create classes to frame database table instance
#################################################
class Cities(db.Model):
    __tablename__ = 'top_airbnb_cities'

    city_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))

    def __repr__(self):
        return '<City %r>' % (self.city)
## end Cities() class

class Nbh_Overview(db.Model):
    __tablename__ = 'neighborhood_overview'

    nbh_id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    walkscore = db.Column(db.Integer)

    def __repr__(self):
        return '<Walkscore %r>' % (self.walkscore)
## end Nbh_Overview() class

class Nbh(db.Model):
    __tablename__ = 'top_neighborhood_overview'

    nbh_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    county = db.Column(db.String(64))
    state = db.Column(db.String(64))

    def __repr__(self):
        return '<Name %r>' % (self.name)
## end Nbh() class

class City_Nbh(db.Model):
    __tablename__ = 'city_nbh'

    nbh_id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<city_nbh %r>' % (self.nbh_id)
## end city_nbh() class


class Census_Crime(db.Model):
    __tablename__ = 'merged_census_crime'

    crime_id = db.Column(db.Integer, primary_key=True)
    nbh_id = db.Column(db.Integer)
    TotalPop = db.Column(db.Integer)
    IncomePerCap = db.Column(db.Integer)
    Crime_RatePer100K = db.Column(db.Float)
    
    def __repr__(self):
        return '<crime_id %r>' % (self.crime_id)
## end Census_Crime() class

#################################################

# Query the database and send the jsonified results
@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "POST":
        city = request.form["city"]
        state = request.form["state"]
        city = Cities(city=city, state=state)
        return redirect("/", code=302)
    return render_template("form.html")
## end send() route

# create route that renders index.html template
@app.route("/")
def home():
    return render_template("index.html")
## end home() route

#################################################
@app.route("/api/cities")
def city():
    
    results = db.session.query(Cities.city_id, Cities.city, Cities.state, City_Nbh.city_id, City_Nbh.nbh_id, Nbh.nbh_id, Nbh.name, Nbh.county)\
        .join(City_Nbh, Cities.city_id==City_Nbh.city_id)\
        .join(Nbh, City_Nbh.nbh_id==Nbh.nbh_id)\
        .all()

    city_id = [result[0] for result in results]
    city = [result[1] for result in results]
    state = [result[2] for result in results]
    nbh_id = [result[5] for result in results]
    nbh_name = [result[6] for result in results]
    county = [result[7] for result in results]

    city_data = [{
        "city_id":city_id, 
        "city": city,
        "state": state,
        "county": county,
        "nbh_id": nbh_id,
        "nbh_name": nbh_name
    }]
    return jsonify(city_data)
## end city() route

#################################################
@app.route("/api/nbh-overview")
def nbh_overview():
    results = db.session.query(Nbh_Overview.nbh_id, Nbh_Overview.latitude, Nbh_Overview.longitude, Nbh_Overview.walkscore, Nbh.name, Nbh.county)\
        .join(Nbh, Nbh_Overview.nbh_id==Nbh.nbh_id)\
        .all()

    nbh_id = [result[0] for result in results]
    nbh_name = [result[4] for result in results]
    lat = [result[1] for result in results]
    lon = [result[2] for result in results]
    walkscore = [result[3] for result in results]
    county = [result[5] for result in results]

    nbh_overview_data = [{
        "nbh_id": nbh_id,
        "nbh_name": nbh_name,
        "lat": lat,
        "lon": lon,
        "walkscore": walkscore,
        "county": county
    }]
    return jsonify(nbh_overview_data)
## end nbh_overview() route


#################################################
@app.route("/api/city-nbh")
def city_nbh():
    results = db.session.query(City_Nbh.nbh_id, City_Nbh.city_id).all()

    nbh_id = [result[0] for result in results]
    city_id = [result[1] for result in results]

    city_nbh_data = [{
        "nbh_id": nbh_id,
        "city_id": city_id
    }]
    return jsonify(city_nbh_data)
## end nbh_overview() route


#################################################
@app.route("/api/census-crime")
def census_crime():
    results = db.session.query(Census_Crime.crime_id, Census_Crime.nbh_id, Census_Crime.TotalPop, Census_Crime.IncomePerCap, Census_Crime.Crime_RatePer100K).all()

    crime_id = [result[0] for result in results]
    nbh_id = [result[1] for result in results]
    total_pop = [result[2] for result in results]
    income_cap = [result[3] for result in results]
    crime_rate = [result[4] for result in results]

    census_crime_data = [{
        "crime_id": crime_id,
        "nbh_id": nbh_id,
        "total_pop": total_pop,
        "income_cap": income_cap,
        "crime_rate": crime_rate
    }]
    return jsonify(census_crime_data)
## end census_crime() route

#################################################
@app.route("/api/ListingInfo<city><nbh>")
def listingsInfo(city_id, nbh_id):

    listingInfo_df = dp.getListingsInfo(city_id, nbh_id)

    listingsInfo =[]
    for index, row in listingInfo_df.iterows():
        
        listings_data = {
            "airbnb_id":row[0], 
            "nbh_id": row[1],
            "city": row[2],
            "state": row[3],
            "coordinates": {
                "lat": row[4],
                "lon": row[5]
                },
            "night_price": row[6],
            "cleaning_fee": row[7]
        }
        listingsInfo.append(listings_data)
    return jsonify(listingsInfo)

## end listingInfo() route

if __name__ == "__main__":
    app.run()