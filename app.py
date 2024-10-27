from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

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
    return jsonify(
        {
            "value": [0, 2, 5, 9, 5, 10, 3, 5, 0, 0, 1, 8, 2, 9, 0],
            "fill": True,
            "gradients": [
                ["#222"],
                ["#42b3f4"],
                ["red", "orange", "yellow"],
                ["purple", "violet"],
                ["#00c6ff", "#F0F", "#FF0"],
                ["#f72047", "#ffd200", "#1feaea"],
            ],
            "selectedGradient": ["#00c6ff", "#F0F", "#FF0"],
            "padding": 8,
            "smooth": True,
            "lineWidth": 2,
        }
    )


# sanity check route
@app.route("/ping", methods=["GET"])
def ping_pong():
    return jsonify("pong!")


if __name__ == "__main__":
    app.run()
