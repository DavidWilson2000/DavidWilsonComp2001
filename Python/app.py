from flask import Flask, jsonify
from flask_restx import Api, Resource
import pyodbc
from datetime import date, datetime

# Flask App and Swagger API initialization
app = Flask(__name__)
api = Api(app, title="Trail API", description="API for managing trails and related data", version="1.0")

# Database connection string
SERVER = 'DIST-6-505.uopnet.plymouth.ac.uk'
DATABASE = 'COMP2001_DWilson'
USERNAME = 'DWilson'
PASSWORD = 'DrvQ278*'
connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

# Define namespaces for the API with hyphens and updated descriptions
ns_users = api.namespace('users', description="Operations related to users")
ns_trails = api.namespace('trails', description="Operations related to trails")
ns_user_trails = api.namespace('user-trails', description="Operations related to user trail associations")
ns_trail_logs = api.namespace('trail-logs', description="Operations related to trail logs")
ns_points = api.namespace('points', description="Operations related to trail points")

def serialize_date(obj):
    """Convert date or datetime objects to ISO 8601 string."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

# Endpoint to get all users
@ns_users.route('/')
class UserList(Resource):
    def get(self):
        try:
            conn = pyodbc.connect(connectionString)
            cursor = conn.cursor()
            SQL_QUERY = """
            SELECT User_id, User_Name, User_Email, User_Role
            FROM CW2.Users
            ORDER BY User_Role ASC;
            """
            cursor.execute(SQL_QUERY)
            records = cursor.fetchall()
            users = [{"ID": r.User_id, "Name": r.User_Name, "Email": r.User_Email, "Role": r.User_Role} for r in records]
            conn.close()
            return jsonify(users)
        except pyodbc.Error as e:
            return {"error": str(e)}, 500

# Endpoint to get all trails
@ns_trails.route('/')
class TrailList(Resource):
    def get(self):
        try:
            conn = pyodbc.connect(connectionString)
            cursor = conn.cursor()
            SQL_QUERY = """
            SELECT trail_id, trail_name, trail_location, length_miles, difficulty, trail_type, description, time_hours
            FROM CW2.Trail;
            """
            cursor.execute(SQL_QUERY)
            records = cursor.fetchall()
            trails = [{"ID": r.trail_id, "Name": r.trail_name, "Location": r.trail_location, "Length (miles)": r.length_miles,
                       "Difficulty": r.difficulty, "Type": r.trail_type, "Description": r.description, "Time (hours)": r.time_hours}
                      for r in records]
            conn.close()
            return jsonify(trails)
        except pyodbc.Error as e:
            return {"error": str(e)}, 500

# Endpoint to get all user-trail associations
@ns_user_trails.route('/')
class UserTrailList(Resource):
    def get(self):
        try:
            conn = pyodbc.connect(connectionString)
            cursor = conn.cursor()
            SQL_QUERY = """
            SELECT User_id, Trail_id, Started_On, Completed_On
            FROM CW2.UserTrail;
            """
            cursor.execute(SQL_QUERY)
            records = cursor.fetchall()
            user_trails = [{"User ID": r.User_id, "Trail ID": r.Trail_id, "Started On": serialize_date(r.Started_On), "Completed On": serialize_date(r.Completed_On)}
                           for r in records]
            conn.close()
            return jsonify(user_trails)
        except pyodbc.Error as e:
            return {"error": str(e)}, 500

# Endpoint to get all trail logs
@ns_trail_logs.route('/')
class TrailLogList(Resource):
    def get(self):
        try:
            conn = pyodbc.connect(connectionString)
            cursor = conn.cursor()
            SQL_QUERY = """
            SELECT log_id, trail_id, added_by_user, added_on
            FROM CW2.TrailLog;
            """
            cursor.execute(SQL_QUERY)
            records = cursor.fetchall()
            trail_logs = [{"Log ID": r.log_id, "Trail ID": r.trail_id, "Added By User": r.added_by_user, "Added On": serialize_date(r.added_on)}
                          for r in records]
            conn.close()
            return jsonify(trail_logs)
        except pyodbc.Error as e:
            return {"error": str(e)}, 500

# Endpoint to get all trail points
@ns_points.route('/')
class PointList(Resource):
    def get(self):
        try:
            conn = pyodbc.connect(connectionString)
            cursor = conn.cursor()
            SQL_QUERY = """
            SELECT trail_id, trail_name, point_id, longitutde, latitude
            FROM CW2.Point;
            """
            cursor.execute(SQL_QUERY)
            records = cursor.fetchall()
            points = [{"Trail ID": r.trail_id, "Trail Name": r.trail_name, "Point ID": r.point_id,
                       "Longitutde": r.longitutde, "Latitude": r.latitude} for r in records]
            conn.close()
            return jsonify(points)
        except pyodbc.Error as e:
            return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
