import datetime
import math
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app

import MySQLdb
import os
import jinja2

# Configure the Jinja2 environment.
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True,
  extensions=['jinja2.ext.autoescape'])

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'earthquake-980:shake'

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body><center><h1><b>Earthquake Hazard Program</b></h1>')
        self.response.out.write('<form action="/earthquake_results" method="POST">')
        self.response.out.write('''<div>Magnitude: <input type="text" name="mag" value=0></div>''')
        self.response.out.write('<br>')
        self.response.out.write('''<div>Location:<input type="text" name="place" value=' '></div>''')
        self.response.out.write('<br>')
        self.response.out.write('''<input type="submit" value="Submit"> </form></center></body></html>''')

class ResultPage(webapp2.RequestHandler):
    def post(self):
        # Handle the post to create a new guestbook entry.
        mag = self.request.get('mag')
        place = self.request.get('place')

        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, port=3306, db='moving', user='root',passwd='') #Used when deployed
        else:
            db = MySQLdb.connect(host='localhost', port=3306, db='moving', user='suyog', passwd='suyog') #used by launcher
            # Alternatively, connect to a Google Cloud SQL instance using:
            # db = MySQLdb.connect(host='ip-address-of-google-cloud-sql-instance', port=3306, db='guestbook', user='root', charset='utf 8')
        self.response.out.write('<html><body><center><h1><b>Earthquake Hazard Program Results</b></h1>')
        self.response.out.write('<br>')
        self.response.out.write('<html><body><center>')
        self.response.out.write('<form action="/"')
        self.response.out.write('<br>')
        self.response.out.write('''<input type="submit" value="Back"> </form></center></body></html>''')

        cursor = db.cursor()
        # Note that the only format string supported is %s
        cursor.execute('''select date(time), place, mag from earthquaked where place like %s and cast(mag as unsigned) = %s;''', ('%'+place+'%', math.ceil(float(mag))))


        quakelist = [];
        for row in cursor.fetchall():
            quakelist.append(dict([('time',row[0]),
                                 ('place',row[1]),
                                 ('mag',row[2])
                                 ]))

        variables = {'quakelist': quakelist}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))
        db.commit()
        db.close()
        self.response.out.write('<br>')
        self.response.out.write('<html><body><center>')
        self.response.out.write('<form action="/"')
        self.response.out.write('<br>')
        self.response.out.write('<input type="submit" value="Back"> </form></center></body></html>')


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/earthquake_results', ResultPage)],
                              debug=True)

def main():
    app = webapp2.WSGIApplication([('/', MainPage),
                                           ('/earthquake_results', ResultPage)],
                                          debug=True)
    run_wsgi_app(app)

if __name__ == "__main__":
    main()