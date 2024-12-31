from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
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

def serialize_date(date_obj):
    if isinstance(date_obj, (datetime, date)):  # Check if the object is a date or datetime
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')  # Format it as a string
    return None  # Handle None or invalid date if necessary

# Define namespaces for the API
ns_users = api.namespace('users', description="Operations related to users")
ns_trails = api.namespace('trails', description="Operations related to trails")
ns_user_trails = api.namespace('user-trails', description="Operations related to user trail associations")
ns_trail_logs = api.namespace('trail-logs', description="Operations related to trail logs")
ns_points = api.namespace('points', description="Operations related to trail points")

# Define Models for Request Payload Validation
user_model = api.model('User', {
    'Name': fields.String(required=True, description='The name of the user'),
    'Email': fields.String(required=True, description='The email of the user'),
    'Role': fields.String(required=True, description='The role of the user')
})

trail_model = api.model('Trail', {
    'Name': fields.String(required=True, description='The name of the trail'),
    'Location': fields.String(required=True, description='The location of the trail'),
    'Length': fields.Float(required=True, description='The length of the trail in miles'),
    'Difficulty': fields.String(required=True, description='The difficulty level of the trail'),
    'Type': fields.String(required=True, description='The type of trail'),
    'Description': fields.String(required=True, description='Description of the trail'),
    'Time': fields.Float(required=True, description='Estimated time to complete the trail in hours')
})

user_trail_model = api.model('UserTrail', {
    'User ID': fields.Integer(required=True, description='The ID of the user'),
    'Trail ID': fields.Integer(required=True, description='The ID of the trail'),
    'Started On': fields.Date(required=True, description='The start date of the trail'),
    'Completed On': fields.Date(required=False, description='The date the trail was completed')
})

trail_log_model = api.model('TrailLog', {
    'Trail ID': fields.Integer(required=True, description='The ID of the trail'),
    'Added By User': fields.Integer(required=True, description='The ID of the user who added the log'),
    'Added On': fields.Date(required=True, description='The date the log was added')
})

point_model = api.model('Point', {
    'Trail ID': fields.Integer(required=True, description='The ID of the trail'),
    'Trail Name': fields.String(required=True, description='The name of the trail'),
    'Longitude': fields.Float(required=True, description='The longitude of the point'),
    'Latitude': fields.Float(required=True, description='The latitude of the point')

})

def execute_query(query, params=(), fetch=False):
    try:
        conn = pyodbc.connect(connectionString)
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            results = cursor.fetchall()
        else:
            conn.commit()
            results = None
        conn.close()
        return results
    except pyodbc.Error as e:
        print(f"Error executing query: {str(e)}")  # Print error for debugging
        raise Exception(f"Database error: {str(e)}")


# Define Models for Request Payload Validation
user_model = api.model('User', {
    'Name': fields.String(required=True, description='The name of the user'),
    'Email': fields.String(required=True, description='The email of the user'),
    'Role': fields.String(required=True, description='The role of the user'),
    'Password': fields.String(required=True, description='The password for the user')
})

# CRUD for Users
@ns_users.route('/')
class Users(Resource):
    def get(self):
        query = "SELECT User_id, User_Name, User_Email, User_Role FROM CW2.Users;"
        users = execute_query(query, fetch=True)
        return jsonify([{"ID": u.User_id, "Name": u.User_Name, "Email": u.User_Email, "Role": u.User_Role} for u in users])

    @api.expect(user_model)
    def post(self):
        data = request.json
        # Ensure a password is provided, or use a default password
        password = data.get('Password', 'defaultPassword123')  # Default password if not provided
        
        query = "INSERT INTO CW2.Users (User_Name, User_Email, User_Role, User_Password) VALUES (?, ?, ?, ?);"
        execute_query(query, (data['Name'], data['Email'], data['Role'], password))
        return {"message": "User created successfully"}, 201

@ns_users.route('/<int:user_id>')
class User(Resource):
    def get(self, user_id):
        query = "SELECT User_id, User_Name, User_Email, User_Role FROM CW2.Users WHERE User_id = ?;"
        users = execute_query(query, (user_id,), fetch=True)
        if users:
            user = users[0]
            return {"ID": user.User_id, "Name": user.User_Name, "Email": user.User_Email, "Role": user.User_Role}
        return {"error": "User not found"}, 404

    @api.expect(user_model)
    def put(self, user_id):
        data = request.json
        query = "UPDATE CW2.Users SET User_Name = ?, User_Email = ?, User_Role = ? WHERE User_id = ?;"
        execute_query(query, (data['Name'], data['Email'], data['Role'], user_id))
        return {"message": "User updated successfully"}

    def delete(self, user_id):
        query = "DELETE FROM CW2.Users WHERE User_id = ?;"
        execute_query(query, (user_id,))
        return {"message": "User deleted successfully"}

# CRUD for Trails
@ns_trails.route('/')
class Trails(Resource):
    def get(self):
        query = "SELECT trail_id, trail_name, trail_location, length_miles, difficulty, trail_type, description, time_hours FROM CW2.Trail;"
        trails = execute_query(query, fetch=True)
        return jsonify([{
            "ID": t.trail_id, "Name": t.trail_name, "Location": t.trail_location,
            "Length (miles)": t.length_miles, "Difficulty": t.difficulty,
            "Type": t.trail_type, "Description": t.description, "Time (hours)": t.time_hours
        } for t in trails])

    @api.expect(trail_model)
    def post(self):
        data = request.json
        query = """INSERT INTO CW2.Trail (trail_name, trail_location, length_miles, difficulty, trail_type, description, time_hours)
                   VALUES (?, ?, ?, ?, ?, ?, ?);"""
        execute_query(query, (data['Name'], data['Location'], data['Length'], data['Difficulty'], data['Type'], data['Description'], data['Time']))
        return {"message": "Trail created successfully"}, 201


@ns_trails.route('/<int:trail_id>')
class Trail(Resource):
    def get(self, trail_id):
        query = "SELECT trail_id, trail_name, trail_location, length_miles, difficulty, trail_type, description, time_hours FROM CW2.Trail WHERE trail_id = ?;"
        trails = execute_query(query, (trail_id,), fetch=True)
        if trails:
            trail = trails[0]
            return {
                "ID": trail.trail_id, "Name": trail.trail_name, "Location": trail.trail_location,
                "Length (miles)": trail.length_miles, "Difficulty": trail.difficulty,
                "Type": trail.trail_type, "Description": trail.description, "Time (hours)": trail.time_hours
            }
        return {"error": "Trail not found"}, 404

    @api.expect(trail_model)
    def put(self, trail_id):
        data = request.json
        query = """UPDATE CW2.Trail SET trail_name = ?, trail_location = ?, length_miles = ?, difficulty = ?, trail_type = ?, description = ?, time_hours = ?
                   WHERE trail_id = ?;"""
        execute_query(query, (data['Name'], data['Location'], data['Length'], data['Difficulty'], data['Type'], data['Description'], data['Time'], trail_id))
        return {"message": "Trail updated successfully"}

    def delete(self, trail_id):
        query = "DELETE FROM CW2.Trail WHERE trail_id = ?;"
        execute_query(query, (trail_id,))
        return {"message": "Trail deleted successfully"}


# CRUD for User-Trails
@ns_user_trails.route('/')
class UserTrails(Resource):
    def get(self):
        query = "SELECT User_id, Trail_id, Started_On, Completed_On FROM CW2.UserTrail;"
        user_trails = execute_query(query, fetch=True)
        return jsonify([{
            "User ID": ut.User_id, "Trail ID": ut.Trail_id, "Started On": serialize_date(ut.Started_On),
            "Completed On": serialize_date(ut.Completed_On)
        } for ut in user_trails])

    @api.expect(user_trail_model)
    def post(self):
        data = request.json
        query = "INSERT INTO CW2.UserTrail (User_id, Trail_id, Started_On, Completed_On) VALUES (?, ?, ?, ?);"
        execute_query(query, (data['User ID'], data['Trail ID'], data['Started On'], data['Completed On']))
        return {"message": "UserTrail association created successfully"}, 201

@ns_user_trails.route('/<int:user_id>/<int:trail_id>')
class UserTrail(Resource):

    @api.expect(user_trail_model)
    def put(self, user_id, trail_id):
        data = request.json
        query = """UPDATE CW2.UserTrail 
                   SET Started_On = ?, Completed_On = ? 
                   WHERE User_id = ? AND Trail_id = ?;"""
        execute_query(query, (data['Started On'], data['Completed On'], user_id, trail_id))
        return {"message": "UserTrail association updated successfully"}

    def delete(self, user_id, trail_id):
        query = "DELETE FROM CW2.UserTrail WHERE User_id = ? AND Trail_id = ?;"
        execute_query(query, (user_id, trail_id))
        return {"message": "UserTrail association deleted successfully"}



# CRUD for Trail-Logs
@ns_trail_logs.route('/')
class TrailLogs(Resource):
    def get(self):
        query = "SELECT log_id, trail_id, added_by_user, added_on FROM CW2.TrailLog;"
        trail_logs = execute_query(query, fetch=True)
        return jsonify([{
            "Log ID": tl.log_id, "Trail ID": tl.trail_id, "Added By User": tl.added_by_user,
            "Added On": serialize_date(tl.added_on)
        } for tl in trail_logs])

    @api.expect(trail_log_model)
    def post(self):
        data = request.json
        query = "INSERT INTO CW2.TrailLog (trail_id, added_by_user, added_on) VALUES (?, ?, ?);"
        execute_query(query, (data['Trail ID'], data['Added By User'], data['Added On']))
        return {"message": "Trail log created successfully"}, 201

@ns_trail_logs.route('/<int:log_id>')
class TrailLog(Resource):

    @api.expect(trail_log_model)
    def put(self, log_id):
        data = request.json
        query = """UPDATE CW2.TrailLog 
                   SET trail_id = ?, added_by_user = ?, added_on = ? 
                   WHERE log_id = ?;"""
        execute_query(query, (data['Trail ID'], data['Added By User'], data['Added On'], log_id))
        return {"message": "Trail log updated successfully"}

    def delete(self, log_id):
        query = "DELETE FROM CW2.TrailLog WHERE log_id = ?;"
        execute_query(query, (log_id,))
        return {"message": "Trail log deleted successfully"}



# CRUD for Points
@ns_points.route('/')
class Points(Resource):
    def get(self):
        # Correct column name: use point_id instead of id
        query = "SELECT trail_id, trail_name, point_id, longitude, latitude FROM CW2.Point;"
        points = execute_query(query, fetch=True)
        return jsonify([{
            "Trail ID": p.trail_id, 
            "Trail Name": p.trail_name, 
            "Point ID": p.point_id, 
            "Longitude": p.longitude, 
            "Latitude": p.latitude
        } for p in points])

    @api.expect(point_model)
    def post(self):
        data = request.json
        query = """
            INSERT INTO CW2.Point (trail_id, trail_name, longitude, latitude)
            VALUES (?, ?, ?, ?);
        """
        try:
            execute_query(query, (data['Trail ID'], data['Trail Name'], data['Longitude'], data['Latitude']))
            return {"message": "Point created successfully"}, 201
        except Exception as e:
            print(f"Error: {e}")  # Log the error for debugging
            return {"error": "Failed to create point. Ensure Point ID is an identity column."}, 500

@ns_points.route('/<int:point_id>')
class Point(Resource):
    def get(self, point_id):
        query = "SELECT trail_id, trail_name, point_id, longitude, latitude FROM CW2.Point WHERE point_id = ?;"
        point = execute_query(query, (point_id,), fetch=True)
        if point:
            p = point[0]
            return {
                "Trail ID": p.trail_id, 
                "Trail Name": p.trail_name, 
                "Point ID": p.point_id, 
                "Longitude": p.longitude, 
                "Latitude": p.latitude
            }
        return {"error": "Point not found"}, 404

    @api.expect(point_model)
    def put(self, point_id):
        data = request.json
        query = """
            UPDATE CW2.Point 
            SET trail_id = ?, trail_name = ?, longitude = ?, latitude = ? 
            WHERE point_id = ?;
        """
        try:
            execute_query(query, (data['Trail ID'], data['Trail Name'], data['Longitude'], data['Latitude'], point_id))
            return {"message": "Point updated successfully"}
        except Exception as e:
            print(f"Error: {e}")
            return {"error": "Failed to update point"}, 500

    def delete(self, point_id):
        query = "DELETE FROM CW2.Point WHERE point_id = ?;"
        execute_query(query, (point_id,))
        return {"message": "Point deleted successfully"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
