# oppapp
Web app for managing Grove City College Media Services' student technician work opportunities. Requires Python 3.

**Signing up for an event:**

![signup](https://cloud.githubusercontent.com/assets/19446736/24306521/455e3a3c-1097-11e7-9214-8accbec515ed.png)


**Events assigned to a tech:**

![myevents](https://cloud.githubusercontent.com/assets/19446736/24306258/6485da88-1096-11e7-8859-ae3bde1913e8.png)


**What the tech coordinator sees:**

![manage](https://cloud.githubusercontent.com/assets/19446736/24306250/58cf70fa-1096-11e7-845d-2f287263fea2.png)


## Installation
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
