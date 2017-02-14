# oppapp
Web app for managing Grove City College Media Services' student tech work opportunities. Requires Python 3.

`$ apt-get install python3 python-pip`

- Using a virtual environment is recommended:
`$ pip install virtualenv
$ virtualenv -p python3 venv
$ source venv/bin/activate`

- Install dependencies:
`$ pip install -r requirements.txt`

- Create the database:
`$ python configure-db.py`

- Run the app:
`$ python app.py`
