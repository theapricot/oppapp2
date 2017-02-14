# oppapp
Web app for managing Grove City College Media Services' student tech work opportunities. Requires Python 3.

`$ apt-get install python3 python-pip`

- Using a virtual environment is recommended: 
`$ pip install virtualenv`

- Clone source, create virtual environment:
```
$ git clone https://github.com/theapricot/oppapp2.git
$ cd oppapp2
$ virtualenv -p python3 venv
$ source venv/bin/activate
```

- Install dependencies:
`$ pip install -r requirements.txt`

- Create the database:
`$ python configure-db.py`

- Run the app:
`$ python app.py`
