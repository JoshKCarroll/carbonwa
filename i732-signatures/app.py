import cgi
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users

import MySQLdb
import os
import jinja2

# Configure the Jinja2 environment.
JINJA_ENVIRONMENT = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
  autoescape=True,
  extensions=['jinja2.ext.autoescape','jinja2.ext.loopcontrols'])

# Define your production Cloud SQL instance information.
_INSTANCE_NAME = 'i732-signatures:voterdb'

class MainPage(webapp2.RequestHandler):
    def get(self):
        
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()

        #Check Authentication
        user = users.get_current_user()
        useremail = user.email()
        cursor.execute('select 1 from users where email = %s', (useremail))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render())
            return
        
        # Create a list of voter entries to render with the HTML.
        voterlist = [];

        variables = {'voterlist': voterlist,
                     'fname':'',
                     'lname':'',
                     'city':'',
                     'county':''}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))

class Results(webapp2.RequestHandler):
    def post(self):
        # Handle the post to get voter results.
        fname = self.request.get('fname')
        lname = self.request.get('lname')
        city = self.request.get('city')
        county = self.request.get('county')
        address = self.request.get('address')
        dob = self.request.get('dob')

        fname = fname.lower()
        lname = lname.lower()
        city = city.lower()
        county = county.lower()
        address = address.lower()
        
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()
        cursor2 = db.cursor()

        #Check Authentication
        user = users.get_current_user()
        useremail = user.email()
        cursor.execute('select 1 from users where email = %s', (useremail))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render())
            return
        
        voterlist = [];
        # Note that the only format string supported is %s
        ##cursor2.execute('select 1 from counties where 1=0;')
        cursor.execute('select 1 from counties where 1=0;')
        if ((cursor.rowcount == 0) and (fname != '') and (lname!='') and (city!='')): 
            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where fname like %s and lname like %s and city like %s limit 300;', (fname, lname, city))
        
        if ((cursor.rowcount == 0) and (fname != '') and (lname!='') and (county!='')): 
            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where fname like %s and lname like %s and county like %s limit 300;', (fname, lname, county))

        if ((cursor.rowcount == 0) and (fname != '') and (lname!='') and (city!='')): 
            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where mname like %s and lname like %s and city like %s limit 300;', (fname, lname, city))

        if ((cursor.rowcount == 0) and (fname != '') and (lname!='') and (county!='')): 
            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where mname like %s and lname like %s and county like %s limit 300;', (fname, lname, county))

        if ((cursor.rowcount == 0) and (fname != '') and (lname!='') and (address!='')):
            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where fname like %s and lname like %s and address like %s limit 300;', (fname, lname, address))

        if ((cursor.rowcount == 0) and (fname != '') and (lname!='') and (dob!='')):
            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where fname like %s and lname like %s and birthdate=%s limit 300;', (fname, lname, dob))

##        if ((cursor.rowcount == 0) and (((fname != '') and (lname!='')) or ((city!='') and (lname!='')))): 
##            cursor.execute('SELECT name, address, city, county, statevoterid from vw_voter where fname like %s and lname like %s limit 300;', (fname, lname))
##            if ((city!='') and (lname!='')):
##                cursor2.execute('SELECT name, address, city, county, statevoterid from vw_voter where city like %s and lname like %s limit 300;', (city, lname))
##            elif ((county!='') and (lname!='')):
##                cursor2.execute('SELECT name, address, city, county, statevoterid from vw_voter where county like %s and lname like %s limit 300;', (county, lname))
##                for row in cursor2.fetchall():
##                  voterlist.append(dict([('name',cgi.escape(row[0])),
##                                     ('address',cgi.escape(row[1])),
##                                     ('city',cgi.escape(row[2])),
##                                     ('county',cgi.escape(row[3])),
##                                     ('statevoterid',cgi.escape(row[4])),
##                                     ]))

        # Create a list of voter entries to render with the HTML.
        for row in cursor.fetchall():
          voterlist.append(dict([('name',cgi.escape(row[0])),
                                 ('address',cgi.escape(row[1])),
                                 ('city',cgi.escape(row[2])),
                                 ('county',cgi.escape(row[3])),
                                 ('statevoterid',cgi.escape(row[4])),
                                 ]))

        variables = {'voterlist': voterlist,
                     'fname':fname,
                     'lname':lname,
                     'city':city,
                     'county':county,
                     'address':address,
                     'dob':dob,
                     'results':'true'}
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))
        db.close()

class Signed(webapp2.RequestHandler):
    def post(self):
        # Handle the post to add a signer.
        statevoterid = self.request.get('signed')
        statevoterid = statevoterid.lower()
        voterlist = [];
        variables = {'voterlist': voterlist,
                     'fname':'',
                     'lname':'',
                     'city':'',
                     'county':'',
                     'statevoterid':statevoterid,
                     'sig':'true'}
        
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()

        #Check Authentication
        user = users.get_current_user()
        useremail = user.email()
        cursor.execute('select 1 from users where email = %s', (useremail))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render())
            return
        
        if(statevoterid != ''):

            cursor.execute('select 1 from signers where statevoterid=%s;', (statevoterid))
            if(cursor.fetchone()):
                variables['dup'] = 'true'
            else:
                cursor.execute('insert into signers (statevoterid, signed, createdby, createddate) VALUES (%s, TRUE, %s, NOW());', (statevoterid, user.email()))

            cursor.execute('select v.name from signers s join vw_voter v on s.statevoterid=v.statevoterid where s.statevoterid=%s limit 1;', (statevoterid))

            for row in cursor.fetchall():
                variables['name'] = cgi.escape(row[0])

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))
        db.commit()
        db.close()

class Invalid(webapp2.RequestHandler):
    def post(self):
        # Handle the post to add an invalid signature.
        fname = self.request.get('fname')
        lname = self.request.get('lname')
        city = self.request.get('city')
        county = self.request.get('county')

        fname = fname.lower()
        lname = lname.lower()
        city = city.lower()
        county = county.lower()
        variables = {'inv_fname':fname,
                     'inv_lname':lname,
                     'invalid':'true'}        
        
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()

        #Check Authentication
        user = users.get_current_user()
        useremail = user.email()
        cursor.execute('select 1 from users where email = %s', (useremail))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render())
            return
        
        if(fname != '' and lname != ''):

            cursor.execute('select 1 from signers where fname=%s and lname=%s and city=%s and county=%s;', (fname, lname, city, county))
            if(cursor.fetchone()):
                variables['dup'] = 'true'
            else:
                cursor.execute('insert into signers (fname, lname, city, county, signed, createdby, createddate) VALUES (%s, %s, %s, %s, FALSE, %s, NOW());', (fname, lname, city, county, user.email()))
        else:
            variables['no_name'] = 'true'
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(variables))
        db.commit()
        db.close()

class Logins(webapp2.RequestHandler):
    def get(self):
        #Check Authentication
        user = users.get_current_user()
        userid = user.user_id()
        
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()

        cursor.execute('select 1 from admins where userid = %s', (userid))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render({'userid':user.user_id()}))
            return

        template = JINJA_ENVIRONMENT.get_template('users.html')
        self.response.write(template.render())
        db.close()

class AddUser(webapp2.RequestHandler):
    def post(self):
        #Check Authentication
        user = users.get_current_user()
        userid = user.user_id()
        emailtoadd = self.request.get('email')

        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()

        cursor.execute('select 1 from admins where userid = %s', (userid))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render({'userid':userid}))
            return

        #usertoadd = users.User("carroll.joshk@gmail.com")
        #idtoadd = usertoadd.user_id()
        cursor.execute('insert into users value ( %s );', (emailtoadd))

        template = JINJA_ENVIRONMENT.get_template('users.html')
        self.response.write(template.render({'emailtoadd':emailtoadd}))
        db.commit()
        db.close()

class Signatures(webapp2.RequestHandler):
    def get(self):
        #Check Authentication
        user = users.get_current_user()
        userid = user.user_id()
        
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):
            db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME, db='voters', user='root', charset='utf8')
        else:
            db = MySQLdb.connect(host='127.0.0.1', port=3306, db='voters', user='root', charset='utf8')

        cursor = db.cursor()

        cursor.execute('select 1 from admins where userid = %s', (userid))
        if not (cursor.fetchone()):
            template = JINJA_ENVIRONMENT.get_template('unauth.html')
            self.response.write(template.render({'userid':user.user_id()}))
            return

        siglist = []

        # Start with the valid signatures
        cursor.execute('SELECT v.name, v.address, v.city, v.county, s.signed, s.createdby, s.createddate from signers s inner join vw_voter v on s.statevoterid=v.statevoterid where signed=TRUE order by s.createddate desc;')
        
        # Create a list of voter entries to render with the HTML.
        for row in cursor.fetchall():
          siglist.append(dict([('name',cgi.escape(row[0])),
                                 ('address',cgi.escape(row[1])),
                                 ('city',cgi.escape(row[2])),
                                 ('county',cgi.escape(row[3])),
                                 ('signed',row[4]),
                                 ('recordedby',cgi.escape(row[5])),
                                 ('recordedon',row[6])
                                 ]))

        # Then append the invalid signatures
        cursor.execute('SELECT concat(fname, " ", lname) as name, "" as address, city, county, signed, createdby, createddate from signers s where signed=FALSE order by s.createddate desc;')
        
        # Create a list of voter entries to render with the HTML.
        for row in cursor.fetchall():
          siglist.append(dict([('name',cgi.escape(row[0])),
                                 ('address',cgi.escape(row[1])),
                                 ('city',cgi.escape(row[2])),
                                 ('county',cgi.escape(row[3])),
                                 ('signed',row[4]),
                                 ('recordedby',cgi.escape(row[5])),
                                 ('recordedon',row[6])
                                 ]))
        
        variables = {'siglist': siglist}
        template = JINJA_ENVIRONMENT.get_template('sigs.html')
        self.response.write(template.render(variables))
        db.close()
        
application = webapp2.WSGIApplication([('/', MainPage),
                               ('/results', Results),
                                ('/signed', Signed),
                                ('/invalid', Invalid),
                                ('/logins', Logins),
                                ('/adduser', AddUser),
                                ('/signatures', Signatures)],
                              debug=True)

def main():
    application = webapp2.WSGIApplication([('/', MainPage),
                                           ('/results', Results),
                                            ('/signed', Signed),
                                            ('/invalid', Invalid),
                                            ('/logins', Logins),
                                            ('/adduser', AddUser),
                                            ('/signatures', Signatures)],
                                          debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
