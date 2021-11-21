from flask import Flask, render_template
from flask_cors import CORS
from flask_restful import Api

from apis_rest import Audio, Text

# sets the root folder for html pages
app = Flask(__name__, template_folder="../app")
# indicates that the service is accessible to anyone
CORS(app, resources={r"/*": {"origins": "*"}})

api = Api(app)
api.add_resource(Audio, "/audio")
api.add_resource(Text, "/text")


# a "get" on the root url will return the html page
@app.route("/")
def _index():
    return render_template("application.html")


if __name__ == "__main__":
    # sets host url to an anonymous one
    app.run(host="0.0.0.0", port=80, debug=True)
