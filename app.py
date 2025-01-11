import os
from flask import Flask
from flasgger import Swagger
from mongodb_connection_manager import MongoConnectionManager
from routes import ads_blue_print

app = Flask(__name__)
Swagger(app) 

# Initialize Database Connection
MongoConnectionManager.initialize_db()

# Register the ads blueprint
app.register_blueprint(ads_blue_print)


if __name__ == '__main__':
    # Set the port for the Flask app (default: 8088)
    port = int(os.environ.get('PORT', 8088))
    app.run(debug=True, port=port)