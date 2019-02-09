# Python SQL toolkit and Object Relational Mapper
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<start><br/>"
        f"/api/v1.0/start_date<start>/end_date<end><br/>"
    )


# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    prcp_data = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date).all()
    prcp = {i[0]:i[1] for i in prcp_data}
    session.close()
    return jsonify(prcp)
        

# Station
@app.route("/api/v1.0/stations")
def stations():

    station_data = session.query(Station.station, Station.name).all()
   # stations = [i[0] for i in station_data]
    session.close()
    return jsonify(station_data)


# Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    
    maxdate = session.query(func.max(Measurement.date)).all()
    max_date = dt.datetime.strptime(maxdate[0][0], '%Y-%m-%d')
    
    max_minus_year = max_date - dt.timedelta(days=365)    

    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.date >= max_minus_year).order_by(Measurement.date.desc()).all()
    
    tobs_data = {i[0]:i[1] for i in results}

    return jsonify(tobs_data)


# Input Start Date and show data after Start Date
@app.route("/api/v1.0/start_date<start>")
def start_dt(start):
    trip_start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= trip_start_date).all()
    if results[0] is None:
        session.close()
        return jsonify({"error": f"Input date : {start} not found."})
    else:
        session.close()
        return jsonify(results)


# Input Start Date and End Date and show data in between those
@app.route("/api/v1.0/start_date<start>/end_date<end>")
def start_end(start,end):
    
    trip_start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    trip_end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    
    if trip_start_date > trip_end_date:
        return jsonify({"error": f"End Date {end} less than Start Date {start}"})
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= trip_start_date).filter(Measurement.date <= trip_end_date).all()
    
    if results[0][0] is None:
        session.close()
        return jsonify({"error": f"Date range {start} and {end} not found in data"}), 404        
    else:
        session.close()
        return jsonify(results)
    
if __name__ == '__main__':
    app.run(debug=True)


