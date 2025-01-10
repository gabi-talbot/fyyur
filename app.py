#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
from datetime import datetime

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment

import logging
from logging import Formatter, FileHandler

from forms import *
from models import db, Venue, Show, Artist

from flask_migrate import Migrate

import collections.abc

collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.app_context().push()
db.init_app(app)
# To allow use of flask-migrate commands
migrate = Migrate(app, db)


# COMPLETED: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    # COMPLETED: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue. Now displayed in template.
    database_venues = Venue.query.distinct('city', 'state').all()

    data = []

    for venue in database_venues:
        datum = {"city": venue.city, "state": venue.state, "venues": []}
        data.append(datum)

    for city in data:
        # query db for venues in same city AND state
        city_venues = Venue.query.filter_by(city=city['city']).all()
        for city_venue in city_venues:
            upcoming_show_count = Show.query.filter_by(venue_id=city_venue.id).filter(Show.start_time > datetime.now()).count()

            venue_data = {"id": city_venue.id, "name": city_venue.name, "num_upcoming_shows": upcoming_show_count}
            city["venues"].append(venue_data)


    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # COMPLETED: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

    response = {
        "count": len(venues),
        "data": []}

    for data in venues:
        show_count = Show.query.filter_by(venue_id=data.id).filter(Show.start_time > datetime.now()).count()
        response["data"].append({
            "id": data.id,
            "name": data.name,
            "num_upcoming_shows": show_count
        })

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # COMPLETED: replace with real venue data from the venues table, using venue_id
    selected_venue = Venue.query.get_or_404(venue_id)


    # query for past and upcoming shows
    past_shows = ((db.session.query(Show, Artist).join(Artist, Show.artist_id==Artist.id)
                  .filter(Show.venue_id == venue_id))
                  .filter(Show.start_time < datetime.now()).all())
    formatted_past_shows = []

    for show in past_shows:
        formatted_show = {}
        formatted_show['artist_id'] = show.Show.artist_id
        formatted_show['artist_name'] = show.Artist.name
        formatted_show['artist_image_link'] = show.Artist.image_link
        formatted_show['start_time'] = str(show.Show.start_time)
        formatted_past_shows.append(formatted_show)


    upcoming_shows = ((db.session.query(Show, Artist).join(Artist, Show.artist_id==Artist.id)
                      .filter(Show.venue_id == venue_id))
                      .filter(Show.start_time > datetime.now()).all())

    formatted_upcoming_shows = []

    for show in upcoming_shows:
        formatted_show = {}
        formatted_show['artist_id'] = show.Show.artist_id
        formatted_show['artist_name'] = show.Artist.name
        formatted_show['artist_image_link'] = show.Artist.image_link
        formatted_show['start_time'] = str(show.Show.start_time)
        formatted_upcoming_shows.append(formatted_show)


    # number of shows for past and upcoming
    past_shows_count = len(formatted_past_shows)
    upcoming_shows_count = len(formatted_upcoming_shows)

    data = {
        "id": selected_venue.id,
        "name": selected_venue.name,
        "city": selected_venue.city,
        "state": selected_venue.state,
        "address": selected_venue.address,
        "phone": selected_venue.phone,
        "image_link": selected_venue.image_link,
        "genres": selected_venue.genres,
        "facebook_link": selected_venue.facebook_link,
        "website": selected_venue.website_link,
        "seeking_talent": selected_venue.seeking_talent,
        "seeking_description": selected_venue.seeking_description,
        "past_shows": formatted_past_shows,
        "upcoming_shows": formatted_upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
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
    # COMPLETED: insert form data as a new Venue record in the db, instead
    # setting csrf to false so that form can validate with a facebook url
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            address = form.address.data
            phone = form.phone.data
            image_link = form.image_link.data
            genres = form.genres.data
            facebook_link = form.facebook_link.data
            website_link = form.website_link.data
            seeking_talent = form.seeking_talent.data
            seeking_description = form.seeking_description.data

            new_venue = Venue(
                name=name, city=city, state=state, address=address, phone=phone,
                image_link=image_link, genres=genres, facebook_link=facebook_link,
                website_link=website_link, seeking_talent=seeking_talent,
                seeking_description=seeking_description
            )
            # Create Venue object and commit to database
            db.session.add(new_venue)
            db.session.commit()

            # COMPLETED: modify data to be the data object returned from db insertion

            # on successful db insert, flash success
            flash('Venue ' + new_venue.name + ' was successfully listed!')
        except:
            db.session.rollback()
            # COMPLETED: on unsuccessful db insert, flash an error instead.
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
            print("error here")
        finally:
            db.session.close()
    else:
        message = []
        for field, error in form.errors.items():
            message.append(field + " : " + error[0])
        flash('Errors occurred: ' + str(message) + ' ' + form.name.data + ' could not be listed')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # COMPLETED: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted')
    except:
        db.session.rollback()
        flash('Venue could not be deleted')
    finally:
        db.session.close()
    return render_template('pages/home.html')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # COMPLETED: replace with real data returned from querying the database
    # Query db for a list of all Artist objects
    artists = Artist.query.all()
    data = []

    # Loop through query and append id and name to data
    for artist in artists:
        artist_data = {}
        artist_data["id"] = artist.id
        artist_data["name"] = artist.name
        data.append(artist_data)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

    # COMPLETED: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()

    response = {
        "count": len(artists),
        "data": []}


    for data in artists:
        show_count = Show.query.filter_by(artist_id=data.id).filter(Show.start_time > datetime.now()).count()
        response["data"].append({
            "id": data.id,
            "name": data.name,
            "num_upcoming_shows": show_count
        })


    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # COMPLETED: replace with real artist data from the artist table, using artist_id
    selected_artist = Artist.query.get_or_404(artist_id)


    # query for past and upcoming shows
    past_shows = ((db.session.query(Show, Venue).join(Venue, Show.venue_id == Venue.id)
                   .filter(Show.artist_id == artist_id))
                  .filter(Show.start_time < datetime.now()).all())

    formatted_past_shows = []

    for show in past_shows:
        formatted_show = {}
        formatted_show['venue_id'] = show.Show.venue_id
        formatted_show['venue_name'] = show.Venue.name
        formatted_show['venue_image_link'] = show.Venue.image_link
        formatted_show['start_time'] = str(show.Show.start_time)
        formatted_past_shows.append(formatted_show)

    upcoming_shows = ((db.session.query(Show, Venue).join(Venue, Show.venue_id == Venue.id)
                   .filter(Show.artist_id == artist_id))
                  .filter(Show.start_time > datetime.now()).all())

    formatted_upcoming_shows = []

    for show in upcoming_shows:
        formatted_show = {}
        formatted_show['venue_id'] = show.Show.venue_id
        formatted_show['venue_name'] = show.Venue.name
        formatted_show['venue_image_link'] = show.Venue.image_link
        formatted_show['start_time'] = str(show.Show.start_time)
        formatted_upcoming_shows.append(formatted_show)

    # number of shows for past and upcoming
    past_shows_count = len(formatted_past_shows)
    upcoming_shows_count = len(formatted_upcoming_shows)

    data = {
        "id": selected_artist.id,
        "name": selected_artist.name,
        "city": selected_artist.city,
        "state": selected_artist.state,
        "phone": selected_artist.phone,
        "image_link": selected_artist.image_link,
        "genres": selected_artist.genres,
        "facebook_link": selected_artist.facebook_link,
        "website": selected_artist.website_link,
        "seeking_venue": selected_artist.seeking_venue,
        "seeking_description": selected_artist.seeking_description,
        "past_shows": formatted_past_shows,
        "upcoming_shows": formatted_upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    # COMPLETED: populate form with fields from artist with ID <artist_id>

    fetched_artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=fetched_artist)
    return render_template('forms/edit_artist.html', form=form, artist=fetched_artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # COMPLETED: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form, meta={'csrf': False})
    artist = Artist.query.get_or_404(artist_id)

    if form.validate():

        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.image_link = form.image_link.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.website_link = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            # on successful db insert, flash success
            db.session.commit()
            flash('Artist ' + artist.name + ' was successfully updated!')

        except:
            db.session.rollback()
            # COMPLETED: on unsuccessful db insert, flash an error instead.
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
        finally:
            db.session.close()

    else:
        message = []
        for field, error in form.errors.items():
            message.append(field + " : " + error[0])
        flash('Errors occurred: ' + str(message) + ' ' + form.name.data + ' could not be edited')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # COMPLETED: populate form with values from venue with ID <venue_id>
    # form = VenueForm(request.form)
    fetched_venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=fetched_venue)

    return render_template('forms/edit_venue.html', form=form, venue=fetched_venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # COMPLETED: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form, meta={'csrf': False})
    venue = Venue.query.get_or_404(venue_id)
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.website_link = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            # on successful db insert, flash success
            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully updated!')

        except:
            db.session.rollback()
            # COMPLETED: on unsuccessful db insert, flash an error instead.
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
        finally:
            db.session.close()
    else:
        message = []
        for field, error in form.errors.items():
            message.append(field + " : " + error[0])
        flash('Errors occurred: ' + str(message) + ' ' + form.name.data + ' could not be edited')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()

    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # COMPLETED: insert form data as a new Venue record in the db, instead
    # setting csrf to false so that form can validate with a facebook url
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():

        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            phone = form.phone.data
            genres = form.genres.data
            facebook_link = form.facebook_link.data
            image_link = form.image_link.data
            website_link = form.website_link.data
            seeking_venue = form.seeking_venue.data
            seeking_description = form.seeking_description.data

            new_artist = Artist(
                name=name, city=city, state=state, phone=phone,
                image_link=image_link, genres=genres, facebook_link=facebook_link,
                website_link=website_link, seeking_venue=seeking_venue,
                seeking_description=seeking_description
            )
            # Create Artist object and commit to database
            db.session.add(new_artist)
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + new_artist.name + ' was successfully listed!')
        except:
            db.session.rollback()
            # COMPLETED: on unsuccessful db insert, flash an error instead.
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
        finally:
            db.session.close()
    else:
        message = []
        for field, error in form.errors.items():
            message.append(field + " : " + error[0])
        flash('Errors occurred: ' + str(message) + ' ' + form.name.data + ' could not be listed')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # COMPLETED: replace with real venues data.

    # join query
    queried_shows = db.session.query(Show, Venue, Artist).join(Venue, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id)
    print(queried_shows)

    # format data for return
    data = []
    for show in queried_shows:
        formatted_show = {"venue_id": show.Show.venue_id, "venue_name": show.Venue.name,
                          "artist_id": show.Show.artist_id, "artist_name": show.Artist.name,
                          "artist_image_link": show.Artist.image_link, "start_time": str(show.Show.start_time)}
        data.append(formatted_show)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # COMPLETED: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form, meta={'csrf': False})
    if form.validate():

        try:
            venue_id = form.venue_id.data
            artist_id = form.artist_id.data
            start_time = form.start_time.data

            new_show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)

            db.session.add(new_show)
            db.session.commit()

            # on successful db insert, flash success
            flash('Show was successfully listed!')
        except:
            print(sys.exc_info())
            db.session.rollback()
            # COMPLETED: on unsuccessful db insert, flash an error instead.
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()
    else:
        message = []
        for field, error in form.errors.items():
            message.append(field + " : " + error[0])
        flash('Errors occurred: ' + str(message) + ' show could not be listed')


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
