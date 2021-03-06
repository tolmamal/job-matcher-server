import time

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api
from flask_mail import Mail

from jobmatcher.server.db import db
from jobmatcher.server.modules.user.User import User
from jobmatcher.server.utils import utils as u
from jobmatcher.config import config
from jobmatcher.server.modules.init_apis import init_apis
from jobmatcher.server.modules.job import scrapUrl
from apscheduler.schedulers.background import BackgroundScheduler

from jobmatcher.server.utils.SOS import locationExtract , job_nltk,pdfFIle
from jobmatcher.server.utils.nltk import job_extract, extract_details
from jobmatcher.server.utils.location import location
from jobmatcher.server.utils.word2vec import matching
from jobmatcher.server.utils.dict_lang_programing import recommendation

app = Flask(__name__)
CORS(app)

app.config['MONGODB_DB'] = config.DB_NAME
app.config['MONGODB_HOST'] = config.DB_SERVER
app.config['MONGODB_PORT'] = config.DB_PORT
app.config['MONGODB_USERNAME'] = config.DB_USERNAME
app.config['MONGODB_PASSWORD'] = config.DB_PASSWORD

app.config['SECRET_KEY'] = config.SECRET_KEY

# init database
db.init_app(app)

# init mail client
app.config.update(
    DEBUG=True,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD
)

# init mail client
mail = Mail(app)

# init flask rest Api
api = Api(app)

@app.route('/api/ping')
def ping():
    return 'Pong: %s' % (time.strftime('%c')), u.HTTP_OK

@app.route('/api/test_job_email')
def test_job_email():
    pdfFIle.makeUserJobsPdf(User.objects[0])

init_apis(api)


def scrape_schedule():
    """
    this function will run in a loop in a set interval
    (defined below inside scheduler.add_job)

    activates scraping function to fetch new jobs information and save it to local DB
    :return:
    """
    # adding new jobs from the web
    scrapUrl.scarpUrl()
    print('schedule')


# https://apscheduler.readthedocs.io/en/latest/
scheduler = BackgroundScheduler()
# possible interval values:
# https://apscheduler.readthedocs.io/en/latest/modules/triggers/interval.html
scheduler.add_job(scrape_schedule, trigger='interval', hours=1)
scheduler.start()


if __name__ == '__main__':
    start_message = 'Job Matcher Server is Running'
    print('@@@@@@@@@@@@@@@@@@@@@@@@')
    print(start_message)
    print('@@@@@@@@@@@@@@@@@@@@@@@@')

    # pdfFIle.convertHtmlToDfdFile('http://localhost:3000/user/5caef73ff0dbb33148fe9c7e#svemtchjbs',
    #                              'chenyair1617@gmail.com','This is the subject',
    #                              'This is the message')
    # scrapUrl.scarpUrl()

    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
