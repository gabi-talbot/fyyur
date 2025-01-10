from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = os.getenv('DEBUG')

# Enable SQL statement generation to be seen in terminal
SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO')

# Connect to the database
# This should be fed in from .env file but have placed here for project marking
# COMPLETED -  IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

