import json

import requests
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

#
url = "https://iwhr.fly.dev/mortgageToInvestment"
headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

# instantiate the app
app = Flask(__name__, static_folder="ui/dist", static_url_path="/")
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return app.send_static_file("index.html")


@app.route("/data")
def data():
    data = {
        "investmentInput": {
            "initialSum": 10000,
            "investmentRate": 23,
            "returnRate": 12
        },
        "mortgageInput": {
            "initialPrice": 20,
            "growthRate": 0.77,
            "downPaymentPercentage": 12
        },
        "purchaseX": 1
    }

    response = requests.post(url, headers=headers, json=data)

    print(response.status_code)
    print(response.json())
    
    return jsonify(
        {
          
    "series": response.json()['graphs'][0]['points'],
    "labels":""


        }
    )


def extract_x_values(json_data):
    # Extract the points from the first graph
    points = json_data['graphs'][0]['points']

    # Create a list of x values
    x_values = [point['x'] for point in points]

    return x_values

# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


if __name__ == "__main__":
    app.run()
