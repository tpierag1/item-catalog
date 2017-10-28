# Item Catalog

This application is an item catalog for Super Ultra Mega Groceries.

The application is written in Flask and contains the following functionality
- Flask application
- Database models for sqlite database
- Database constructor
- Bootstrap style sheets
- HTML templates 

The application will allow the user to do the following:
- View items in the catalog by category
- Add categories
- Edit categories
- Delete Categories
- Add items to categories
- Delete items in categories
- Edit items in categories
- Login and Logout using Google OAuth API
- Make API calls for category listings and items in categories

Functionality to add, delete and edit items and categories are protected through 
authentication checks.

## Setup

These instructions have been tested on Ubuntu 16.04

#### Install Dependencies
`apt update`<br>
`apt install make zip unzip postgresql`<br>
`apt-get -qqy install python python-pip`<br>
`pip2 install --upgrade pip`<br>
`pip2 install flask packaging oauth2client redis passlib flask-httpauth`<br>
`pip2 install sqlalchemy flask-sqlalchemy psycopg2 bleach requests`<br>


#### Download and Install Redis
`wget http://download.redis.io/redis-stable.tar.gz`<br>
`tar xvzf redis-stable.tar.gz`<br>
`cd redis-stable`<br>
`make`<br>
`make install`<br>

#### Setup Google OAuth API
- Register Google Account
- Go to [Google API Console](https://console.developers.google.com)
- Login
- Click on the logo next to the Google APIs logo on the top left of the page
- Create a new project
- Go back to the project menu and select the project
- Click on Credentials on the menu on the left of the screen
- Click on Create Credentials
- Select OAuth Client ID
- Click on Configure Consent Screen
- Fill out the Product Name and click Save
- On the following screen select Web Application
- For Authorized Javascript Origin put http://localhost:8000 if running locally.  
  Substitute a domain name or IP for localhost if running remotely.
  This will have to be the domain or IP that will be calling to Google
- For Authorized Redirect URIs put in http://localhost:8000/gconnect
  Substitute the relevant IP or URL as in the Authorized Javascript Origin field
 - Click Save
 - On the main project screen click the Download icon to download the client_secrets JSON file
 - Download and rename the file client_secrets.json
 - Move the file to the project directory
 - Copy the Client ID from the Google project panel
 - Paste the ID into the templates/login.html file here:<br>
  ```
  <script>
        gapi.load('auth2', function() {
            auth2 = gapi.auth2.init({
                client_id: '[ADD CLIENT_ID HERE]',
                });
            });
   </script>
   ```
  
  ## Running Application
  
  To run the application the database needs to be populated.
  To do so run the db_constructor.py script<br>
  `python db_constructor.py`
  
  Start Redis<br>
  `redis-server`
  
  Open a new Terminal tab and run the application<br>
  `python application.py`
  
  To access the application go to http://localhost:8000






