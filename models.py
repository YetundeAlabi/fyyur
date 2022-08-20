from app import app
# from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy(app)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column((db.String), nullable=False)
    city = db.Column((db.String(120)), nullable=False)
    state = db.Column((db.String(120)), nullable=False)
    address = db.Column((db.String(120)), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    image_link = db.Column((db.String(500)), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    genres = db.Column((db.ARRAY(db.String)), nullable=False)
    seeking_talent = db.Column((db.Boolean), nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", backref="venues", lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column((db.String), nullable=False)
    city = db.Column((db.String(120)), nullable=False)
    state = db.Column((db.String(120)), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    genres = db.Column((db.ARRAY(db.String)), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))   
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column((db.Boolean), nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref="artists", lazy=True)
    
class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time} "
 