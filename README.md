# Abuse-Mailbox-Dashboard
> Byambadalai Sumiya | May 25th 2020
-----------------

<p align="center"> <i>Homepage of webserver builds charts with processed data </i> </p> 
<p align="center" style="width:400px"><img src="https://github.com/ByamB4/Abuse-Mailbox-Dashboard/blob/master/public/img/homepage-1.png" style="width:400px"></p>
<p align="center" style="width:400px"><img src="https://github.com/ByamB4/Abuse-Mailbox-Dashboard/blob/master/public/img/homepage-2.png" style="width:400px"></p>

<p align="center"> <i>View <u><b>actionable dashboard</b></u> from your abuse mailbox</i> </p> 
<p align="center" style="width:400px"><img src="https://github.com/ByamB4/Abuse-Mailbox-Dashboard/blob/master/public/img/actionpage-1.png" style="width:400px"></p>

Getting Started
===============
1) `git clone https://github.com/ByamB4/Abuse-Mailbox-Dashboard`
2) `source backend/env/bin/activate`
3) `pip3 install -r backend/requirements.txt`
3) `python3 backend/src/manage.py runserver`
4) Open your browser `localhost:8000`

Setup
===============
1) Configure local variables

  * `export EMAIL_USERNAME='abuse@yourdomain'`
  * `export EMAIL_PASSWORD='yoursupersecret'`
  * `export SECRET_KEY='50h$whpv47sknlsufsl^t)t)y0vr6s+b++do48ml_pa!8dyd!s@r50'` for django, make sure its different


Quick Demo
===============

1) If its first time running it will download mails and processing data from it _(takes some time)_

<p align="center"><img src="https://github.com/ByamB4/Abuse-Mailbox-Dashboard/blob/master/public/gif/downloading-mails.gif"></p>

2) After downloaded all mails it will produce data from each mail take a look at [code](https://github.com/ByamB4/Abuse-Mailbox-Dashboard/blob/master/backend/src/main/generator/run.py)

<p align="center"><img src="https://github.com/ByamB4/Abuse-Mailbox-Dashboard/blob/master/public/gif/processing-mails.gif"></p>

3) If everything fine. It's looks like first homepage image

Quick Note
===============
1) Make sure open it latest browser

