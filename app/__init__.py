import json
import logging.config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from geoalchemy2 import Geometry
from flask_sqlalchemy import SQLAlchemy
from safrs import SAFRSBase, SAFRSAPI
from safrs.json_encoder import SAFRSJSONEncoder
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape
from shapely import geometry
from geoalchemy2.elements import _SpatialElement
#from flask_migrate import Migrate
import safrs

db = safrs.DB

#migrate = Migrate()

class GeoJSONEncoder(SAFRSJSONEncoder):
    """
        json encode geometry shapes
    """
    def default(self, obj, **kwargs):
        if isinstance(obj, _SpatialElement):
            result = geometry.mapping(to_shape(obj))
            return result

        return super().default(obj, **kwargs)


class DocumentedColumn(db.Column):
    """
        The class attributes are used for the swagger
    """

    description = "Geo column description"
    swagger_type = "json"
    swagger_format = "json"
    sample = {"coordinates": [-122.43129, 37.773972], "type": "Point"}


class City(SAFRSBase, db.Model):
    """
        A city, including its geospatial data
    """

    __tablename__ = "cities"

    point_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(30),default="Gotham City")
    geo = DocumentedColumn(Geometry(geometry_type="POINT", srid=25833, dimension=2))

    def __init__(self, *args, **kwargs):
        # convert the json to geometry database type
        geo = kwargs.get("geo")
        kwargs["geo"] = str(to_shape(from_shape(geometry.shape(geo))))
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"<City {self.location}"

    __str__ = __repr__

    def get_cities_within_radius(self, radius):
        """Return all cities within a given radius (in meters) of this city."""
        return City.query.filter(func.ST_Distance_Sphere(City.geo, self.geo) < radius).all()


def connect_to_db(app):
    """Connect the database to Flask app."""

    #app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///testgis"
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def create_api(app, HOST="localhost", PORT=5000, API_PREFIX=""):
    api = SAFRSAPI(app, host=HOST, port=PORT, prefix=API_PREFIX)
    app.json_encoder = GeoJSONEncoder
    geo = {
          "coordinates": [
            -122.4111,
            37.6305
          ],
          "type": "Point"
        }
    test_city = City(location='Test City', latitude=38.01, longitude=-122.4111, geo=geo)
    db.session.add(test_city)
    db.session.commit()
    api.expose_object(City)
    safrs.log.info(f"Starting API: http://{HOST}:{PORT}/{API_PREFIX}")



def create_app():
    """This app factory omits starting SAFRSAPI to enable running the shell etc in a simpler way"""
    app = Flask("some-api")
    app.config.from_envvar("CONFIG_MODULE")
    logging.config.dictConfig(app.config.get("LOGGING", {}))
    db.init_app(app)
    #migrate.init_app(app, db)
    return app


def run_app():
    app = create_app()
    with app.app_context():
        create_api(app, app.config["SWAGGER_HOST"], app.config["SWAGGER_PORT"])
    return app

