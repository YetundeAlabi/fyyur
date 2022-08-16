#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.mime import application
import json
import datetime
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column((db.String), nullable=False)
    city = db.Column((db.String(120)), nullable=False)
    state = db.Column((db.String(120)), nullable=False)
    address = db.Column((db.String(120)), nullable=False)
    phone = db.Column((db.String(120)), nullable=False)
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
    phone = db.Column((db.String(120)), nullable=False)
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
    
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    venues = Venue.query.with_entities(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    for venue in venues:
        venues_cities = Venue.query.with_entities(Venue.id, Venue.name).filter_by(city=venue[0]).filter_by(state=venue[1])
        formatted_venues = []
        for v in venues_cities:
            show_count = Show.query.filter_by(venue_id=v.id).filter(Show.start_time > datetime.now()).count()
            formatted_venues.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": show_count
        })
        data.append({"city": venue[0], "state": venue[1], "venues": formatted_venues})
    return render_template('pages/venues.html', areas=data);
  
 
@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get("search_term", "")
    venues_search = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    venue_unit = []
    for venue in venues_search:   
        venue_unit.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()
            })
    response = {"count": len(venues_search),
                "data": venue_unit}
    return render_template('pages/search_venues.html', results=response, search_term=search_term)
     
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    shows = venue.shows
    past_shows = []
    upcoming_shows = []
    for show in shows:
        artist_details = {
            "artist_id": show.artist_id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if datetime.now() > show.start_time:
            past_shows.append(artist_details)
        else:
            upcoming_shows.append(artist_details)
            
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }  
    return render_template('pages/show_venue.html', venue=data)
   
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = VenueForm(request.form)

    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
    )
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info)
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        
    return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!.')
    except:
        db.session.rollback()
        flash('Venue ' + venue.name + ' could be not deleted.')
    finally:
        db.session.close()
    
    return redirect(url_for('index'))
        
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=data)

 
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    artist_search = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = []
    for artist in artist_search:
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.now()).count(),
        })
      
    response = {
        "count": len(artist_search),
        "data": data,
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

 
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    shows = artist.shows
    upcoming_shows = []
    past_shows = []
    
    for show in shows:
        venue_details ={
          "venue_id": show.venue_id,
          "venue_name": show.venues.name,
          "venue_image_link": show.venues.image_link,
          "start_time": format_datetime(str(show.start_time)), 
        }
        if show.start_time > datetime.now():
            upcoming_shows.append(venue_details)
        else:
            past_shows.append(venue_details)
      
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    } 
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    data = Artist.query.get(artist_id)
    artist = {
        "id": data.id,
        "name": data.name,
        "genres": data.genres,
        "city": data.city,
        "state": data.state,
        "phone": data.phone,
        "website": data.website_link,
        "facebook_link": data.facebook_link,
        "seeking_venue": data.seeking_venue,
        "seeking_description": data.seeking_description,
        "image_link": data.image_link,
    }
    
    form = ArtistForm(formdata=None, data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    try:
    
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.city=form.city.data
        artist.state=form.state.data
        artist.phone=form.phone.data
        artist.genres=form.genres.data 
        artist.facebook_link=form.facebook_link.data
        artist.image_link=form.image_link.data
        artist.seeking_venue=form.seeking_venue.data
        artist.seeking_description=form.seeking_description.data
        artist.website_link=form.website_link.data

        db.session.add(artist)
        db.session.commit()
        flash("Artist " + artist.name + " was successfully edited!")
    except:
        db.session.rollback()
        flash("An error occurred. Artist " + artist.name + " could not be listed")
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

   
    
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    data = Venue.query.get(venue_id)
    venue ={
            "id": data.id,
            "name": data.name,
            "genres": data.genres,
            "address": data.address,
            "city": data.city,
            "state": data.state,
            "phone": data.phone,
            "website": data.website_link,
            "facebook_link": data.facebook_link,
            "seeking_talent": data.seeking_talent,
            "seeking_description": data.seeking_description,
            "image_link": data.image_link,
        }
    return render_template('forms/edit_venue.html', form=form, venue=venue)

 
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    try:
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city=form.city.data
        venue.state=form.state.data
        venue.address=form.address.data
        venue.phone=form.phone.data
        venue.genres=form.genres.data
        venue.facebook_link=form.facebook_link.data
        venue.image_link=form.image_link.data
        venue.seeking_talent=form.seeking_talent.data
        venue.seeking_description=form.seeking_description.data
        venue.website_link=form.website_link.data
        db.session.add(venue)
        db.session.commit()
        flash('Venue '+ venue.name + ' was successfully edited!')
    except:
        db.session.rollback()
        flash('Venue '+ venue.name + ' could not be edited!')

    finally:
        db.session.close()
        
    return redirect(url_for('show_venue', venue_id=venue_id))

 
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:

        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
    )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
        
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venues.name,
            "artist_id": show.artist_id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": format_datetime(str(show.start_time))
        })
        
    return render_template('pages/shows.html', shows=data)

 
@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')
  
 
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
