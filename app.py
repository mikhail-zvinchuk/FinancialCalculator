import json
import logging
from datetime import datetime
import requests
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sys
from logging.handlers import RotatingFileHandler

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create formatters
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_formatter)

# File Handler
file_handler = RotatingFileHandler('api_requests.log', maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Prevent Flask's default logger from duplicating messages
logging.getLogger('werkzeug').handlers = []

# Test logging
logger.debug("Debug messages will now be visible")
logger.info("Info messages are visible")
logger.warning("Warning messages are visible")

# External API configuration
MORTGAGE_CALC_API = "https://iwhr.fly.dev/mortgageToInvestment"
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


@app.route("/data", methods=["GET", "POST"])
def data():
    try:
        request_time = datetime.now()
        logger.info("=" * 80)
        logger.info(f"New request received at {request_time}")

        if request.method == "GET":
            # Handle GET request with query parameters
            if not request.args:
                logger.info("GET request received without parameters - using default values")
                # Use default values
                investment_input = {
                    "initialSum": 100000,
                    "investmentRate": 0.10,  # 10%
                    "returnRate": 0.07  # 7%
                }
                mortgage_input = {
                    "initialPrice": 500000,
                    "growthRate": 0.03,  # 3%
                    "downPaymentPercentage": 0.20  # 20%
                }
            else:
                try:
                    investment_input = {
                        "initialSum": float(request.args.get("initialSum", 100000)),
                        "investmentRate": float(request.args.get("investmentRate", 10)) / 100,
                        "returnRate": float(request.args.get("returnRate", 7)) / 100
                    }
                    mortgage_input = {
                        "initialPrice": float(request.args.get("initialPrice", 500000)),
                        "growthRate": float(request.args.get("growthRate", 3)) / 100,
                        "downPaymentPercentage": float(request.args.get("downPaymentPercentage", 20)) / 100
                    }
                except (TypeError, ValueError) as e:
                    error_msg = f"Invalid parameters in GET request: {str(e)}"
                    logger.error(error_msg)
                    return jsonify({"error": error_msg}), 400

        else:  # POST request
            # Check if we have JSON data
            if not request.is_json:
                logger.info("POST request received without JSON data - returning error")
                return jsonify({
                    "error": "No JSON data provided"
                }), 400

            # Get JSON data
            data = request.get_json()
            logger.debug(f"Raw request data: {json.dumps(data, indent=2)}")

            # Validate investment parameters
            try:
                investment_input = data.get('investmentInput', {})
                if not all(key in investment_input for key in ['initialSum', 'investmentRate', 'returnRate']):
                    raise ValueError("Missing required investment parameters")
                logger.debug(f"Parsed investment input: {investment_input}")
            except (TypeError, ValueError) as e:
                error_msg = f"Invalid investment parameters: {str(e)}"
                logger.error(f"Investment parameter parsing failed: {error_msg}")
                logger.error(f"Raw data was: {json.dumps(data, indent=2)}")
                return jsonify({"error": error_msg}), 400

            # Validate mortgage parameters
            try:
                mortgage_input = data.get('mortgageInput', {})
                if not all(key in mortgage_input for key in ['initialPrice', 'growthRate', 'downPaymentPercentage']):
                    raise ValueError("Missing required mortgage parameters")
                logger.debug(f"Parsed mortgage input: {mortgage_input}")
            except (TypeError, ValueError) as e:
                error_msg = f"Invalid mortgage parameters: {str(e)}"
                logger.error(f"Mortgage parameter parsing failed: {error_msg}")
                logger.error(f"Raw data was: {json.dumps(data, indent=2)}")
                return jsonify({"error": error_msg}), 400

        # Prepare request payload
        payload = {
            "investmentInput": investment_input,
            "mortgageInput": mortgage_input
        }

        # Add optional purchaseX if provided
        if request.method == "POST" and "purchaseX" in data:
            payload["purchaseX"] = data["purchaseX"]
            logger.debug(f"Added purchaseX: {payload['purchaseX']}")
        elif request.method == "GET" and "purchaseX" in request.args:
            try:
                payload["purchaseX"] = int(request.args.get("purchaseX"))
                logger.debug(f"Added purchaseX: {payload['purchaseX']}")
            except ValueError:
                pass  # Ignore invalid purchaseX in GET request

        # Log outgoing request
        logger.info(f"Sending request to external API at {MORTGAGE_CALC_API}")
        logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

        try:
            logger.debug("Making API request...")
            response = requests.post(MORTGAGE_CALC_API, headers=headers, json=payload, timeout=10)
            logger.debug(f"API response status code: {response.status_code}")
            response.raise_for_status()
            
            # Log raw response for debugging
            logger.debug(f"Raw API response: {response.text[:1000]}...")  # Log first 1000 chars to avoid huge logs
            
        except requests.exceptions.Timeout:
            error_msg = "External API request timed out (10s limit)"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 504
        except requests.exceptions.RequestException as e:
            error_msg = f"External API request failed: {str(e)}"
            logger.error(f"API request failed: {error_msg}")
            logger.error(f"Request was: {json.dumps(payload, indent=2)}")
            return jsonify({"error": error_msg}), 502

        # Log API response timing
        response_time = datetime.now() - request_time
        logger.info(f"External API response received in {response_time.total_seconds():.2f}s")

        try:
            api_response = response.json()
            logger.debug(f"Parsed API response: {json.dumps(api_response, indent=2)}")
            
            if "graphs" not in api_response:
                error_msg = "Invalid response format from external API"
                logger.error(f"{error_msg}: {json.dumps(api_response, indent=2)}")
                return jsonify({"error": error_msg}), 502

            # Transform and return the response
            result = {
                "series": [
                    {
                        "identifier": graph["identifier"],
                        "points": [
                            {"x": float(point["x"]), "y": float(point["y"])}
                            for point in graph["points"]
                        ]
                    }
                    for graph in api_response["graphs"]
                ]
            }

            # Log the transformed response
            logger.info(f"Successfully processed response with {len(result['series'])} series")
            logger.debug(f"Series identifiers: {[s['identifier'] for s in result['series']]}")
            logger.debug(f"Points per series: {[len(s['points']) for s in result['series']]}")
            
            # Log a sample of points from each series
            for series in result['series']:
                points_sample = series['points'][:3]  # First 3 points
                logger.debug(f"Sample points for {series['identifier']}: {points_sample}")

            # Validate the response format
            if not result['series'] or not all(s.get('points') for s in result['series']):
                error_msg = "Invalid response format: missing points in series"
                logger.error(error_msg)
                return jsonify({"error": error_msg}), 502

            return jsonify(result)

        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"Error processing API response: {str(e)}"
            logger.error(f"Response processing failed: {error_msg}")
            logger.error(f"Raw response was: {response.text[:1000]}...")  # Log first 1000 chars
            return jsonify({"error": error_msg}), 502

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error occurred: {error_msg}")
        logger.exception("Full traceback:")  # This will log the full stack trace
        return jsonify({"error": error_msg}), 500


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
