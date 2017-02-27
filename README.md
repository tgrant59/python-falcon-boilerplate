# Odin
The boostrapping for a Python REST API. Part of the Valhalla Project


## The Odin Stack

##### Web Framework
- [Falcon](https://falcon.readthedocs.io/en/stable/)

##### Database
- Relational Database - [MySQL](https://dev.mysql.com/doc/) with [Peewee ORM](http://peewee.readthedocs.io/en/latest/index.html)
- NoSQL Database - [MongoDB](https://docs.mongodb.com/manual/) with [PyMongo](https://api.mongodb.com/python/current/)
- In-Memory Cache - [Redis](http://redis.io/documentation) with [redis-py](https://redis-py.readthedocs.io/en/latest/)

##### Cloud
- [Amazon Web Services](https://aws.amazon.com/documentation/) with [Boto3](https://boto3.readthedocs.io/en/latest/)

##### Payment Processing
- [Stripe](https://stripe.com/docs) - [Python API Docs](https://stripe.com/docs/api/python)

##### HTML Templating
- [Jinja2](http://jinja.pocoo.org/docs/dev/)

##### Asynchronous Tasking
- [Celery](http://docs.celeryproject.org/en/latest/)


## Installation

### Dependencies
1. [Docker](https://www.docker.com/)

### How to Install

1. Clone the repository, copy it, remove the original repo, and change to your new project
    ```bash
    git clone git@github.com:tgrant59/Odin.git
    cp -r Odin example-project-name
    rm -rf Odin
    cd Odin
    ```
    
### Configure your installation
Your main configuration file is `app/utils/config.py`. You will change many of the configuration parameters here. Some recommended ones are outlined below. Remember that this is your development configuration file, so you shouldn't put production values here.

##### Set Your Database Names
- Set the names of your MySQL and MongoDB databases in the config file
- Change the MySQL initialization script (`dev/init/init-mysql.sh`) to use the correct MySQL database name

##### Configure Email Addresses
- Set the addresses in the **Email config** section
- Set the **ADMINS** and the **SERVER_EMAIL** in the **CELERY** config

##### Configure Stripe
- Set your Stripe test token
- Define your Stripe plans

## Usage

##### Celery
- By default, Strappy comes configured to run 2 queues: the default _'celery'_ queue and a _'priority'_ queue. The mailing tasks are configured to run in the _'priority'_ queue.
