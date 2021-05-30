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

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    # Convert list of tuples into normal list
    precipitation_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict['Precipitation'] = prcp
        
        precipitation_data.append(prcp_dict)
  
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    # /api/v1.0/stations
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    results = session.query(Station.station,Station.name).all()
    session.close()

    stations_data = []
    for station, name in results:
        station_dict = {}
        station_dict['Station'] = station
        station_dict['Name'] = name
        stations_data.append(station_dict)
    return jsonify(stations_data)

@app.route('/api/v1.0/tobs')
def temperature():
    # Query the dates and temperature observations of the most active station for the last year 
    # of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)
    active_station = session.query(Measurement.station,func.count(Measurement.station))\
    .group_by(Measurement.station).order_by((func.count(Measurement.station).desc())).first()
    #Determine the interval of the 
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    
    split_date = recent_date.split('-')
    date_f = dt.datetime(int(split_date[0]),int(split_date[1]),int(split_date[2]))
    date_i = dt.datetime(int(split_date[0])-1,int(split_date[1]),1)



    results = session.query(Measurement.id,Measurement.station, \
        Measurement.date,Measurement.prcp,Measurement.tobs).\
        filter(Measurement.date >= date_i).all()


    temperatures = []
    for id, station, date, prcp,tobs in results:
        dict_temp = {}
        dict_temp['ID'] = id
        dict_temp['Station'] = station
        dict_temp['Precipitation'] = prcp
        dict_temp['Date'] = date
        dict_temp['Temperature'] = tobs
        temperatures.append(dict_temp)

    session.close()
   
    
    return jsonify(temperatures)




if __name__ == '__main__':
    app.run(debug=True)