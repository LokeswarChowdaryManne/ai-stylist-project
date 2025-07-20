from flask import Flask, jsonify, request
from stylist import Stylist # Import your Stylist class from stylist.py

# Create an instance of the Flask application
app = Flask(__name__)

# Create a single instance of the Stylist when the server starts
personal_stylist = Stylist()

# Define a "route" for our API endpoint
@app.route("/suggest")
def get_outfit_suggestion():
    # Get parameters from the URL (e.g., ?occasion=Formal&temp=25)
    occasion = request.args.get('occasion', type=str)
    temp = request.args.get('temp', type=int)

    # Basic validation
    if not occasion or temp is None:
        return jsonify({"error": "Missing required parameters: occasion and temp"}), 400

    # Use our Stylist class to get an outfit
    outfit = personal_stylist.get_suggestion(occasion.capitalize(), temp)

    # Return the outfit as a JSON response
    if outfit:
        return jsonify(outfit)
    else:
        return jsonify({"message": "No suitable outfit found."}), 404

# You can keep the old hello_world route for basic testing
@app.route("/")
def hello_world():
    return "<h1>Stylist Backend is running. Use the /suggest endpoint.</h1>"

# This allows us to run the server by executing this file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)