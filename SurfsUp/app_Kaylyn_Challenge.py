
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

############################################
# Creating connection to Hawaii.sqlite file
############################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

###########################################
# Flask
###########################################

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations List: /api/v1.0/stations<br/>"
        f"Temp. for One Year: /api/v1.0/tobs<br/>"
        f"Temp Stat from the Start Date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temp Stat from Start to Finish Dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/<start>')
def start_data(start):
    session = Session(engine)
    query_r = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    start_tobs_a = []
    for min,avg,max in query_r:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_a.append(tobs_dict)

    return jsonify(start_tobs_a)

@app.route('/api/v1.0/<start>/<stop>')
def start_and_stop(start,stop):
    session = Session(engine)
    query_r = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    start_stop_tobs_a = []
    for min,avg,max in query_r:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_a.append(tobs_dict)

    return jsonify(start_stop_tobs_a)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latest_str = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_str, '%Y-%m-%d')
    query_date = dt.date(latest_date.year -1, latest_date.month, latest_date.day)
    sta = [Measurement.date,Measurement.tobs]
    query_r = session.query(*sta).filter(Measurement.date >= query_date).all()
    session.close()

    tobs_a = []
    for date, tobs in query_r:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_a.append(tobs_dict)

    return jsonify(tobs_a)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sta = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    query_r = session.query(*sta).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in query_r:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sta = [Measurement.date,Measurement.prcp]
    query = session.query(*sta).all()
    session.close()

    precipitation = []
    for date, prcp in query:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

if __name__ == '__main__':
    app.run(debug=True)
