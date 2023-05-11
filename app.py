# Import the dependencies.

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base= automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

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


#Query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    y_precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-24").\
        filter(Measurement.date <= "2017-08-23").all()
    
    session.close()

    #Dictionary using date as the key and prcp as the value.    
    precipitation_l= []
    for date,prcp in y_precipitation:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precipitation_l.append(precip_dict)

    #Return the JSON representation of your dictionary.
    return jsonify(precipitation_l)

#Query stations route: jsonified data of all of the stations in the database

@app.route("/api/v1.0/stations")
def stations():
    sel=[Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    all_stations= session.query(*sel).all()

    session.close()

    #Converting list of touples into normal list
    #station_l= list(np.ravel(all_stations))
    #creating Dictionary to better display data
    station_all= []
    for station, name, lat, lon, elevation in all_stations:
        station_dict= {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Latitude"] = lat
        station_dict["Longitude"] = lon
        station_dict["Elevation"] = elevation
        station_all.append(station_dict)

    #Return JSON
    return jsonify(station_all)

#Query most active station (USC00519281) last year of data. hard code (USC00519281) in the filter and remove variable

@app.route("/api/v1.0/tobs")
def tobs():
    #most_active_station= 'USC00519281'
    results=session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= "2016-08-24").\
    filter(Measurement.date <= "2017-08-23").\
    filter(Measurement.station == 'USC00519281').all()

    session.close()

    #Dictionary using date as the key and prcp as the value.    
    tobs_most= []
    for date,tobs in results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Temp"] = tobs
        tobs_most.append(tobs_dict)
    #Return json
    return jsonify(tobs_most)

#Query with start date as parameter from URL 
# Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset 

@app.route("/api/v1.0/<start>")
def temp_start(start):
    results= session.query(func.min(Measurement.tobs),
                           func.max(Measurement.tobs),
                           func.avg(Measurement.tobs)).\
                           filter(Measurement.date >= start).all()
    session.close()

    #Creating dictionary to json
    #tempstart= []
    #for min,max,avg in results:
        #temp_dict= {}
        #temp_dict['TMIN'] = min
        #temp_dict['TMAX'] = max
        #temp_dict['TAVG'] = avg
        #tempstart.append(temp_dict)
    #Following dictionary was created with chat GPT assistance.
    temps_dict={'TMIN': results[0][0], 'TMAX': results[0][1], 'TAVG': results[0][2]}
    #Return json
    #return jsonify(tempstart)
    return jsonify(temps_dict)
#Query with start date and end date as parameters from URL 
# Returns the min, max, and average temperatures calculated from the given start date to the end date.

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    results_s_e= session.query(func.min(Measurement.tobs),
                           func.max(Measurement.tobs),
                           func.avg(Measurement.tobs)).\
                           filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    #Create dictionary to json
    tempstart_end= []
    for min, max, avg in results_s_e:
        temp_dict_se= {}
        temp_dict_se['TMIN']= min
        temp_dict_se['TMAX']= max
        temp_dict_se['TAVG']= avg
        tempstart_end.append(temp_dict_se)
    #Return json
    return jsonify(tempstart_end)

if __name__== '__main__':
    app.run(debug=True)


session.close()