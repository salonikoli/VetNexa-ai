from flask import Flask, render_template
from flask_cors import CORS
from dogs.routes import bp as dogs_bp
from poultry.routes import bp as poultry_bp

from cattle.routes import bp as cattle_bp
from goats.routes import bp as goats_bp

from auth_routes import auth_bp
import os

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)

# Register blueprints with prefixes
app.register_blueprint(dogs_bp, url_prefix="/dogs")
app.register_blueprint(poultry_bp, url_prefix="/poultry")
app.register_blueprint(cattle_bp, url_prefix="/cattle")
app.register_blueprint(goats_bp, url_prefix="/goats")
app.register_blueprint(auth_bp, url_prefix="/auth")

@app.route("/")
def home():
    return render_template("index.html")

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=False)

