import yaml
import os
import uuid
import json
import importlib
import re
import requests
import logging
import asynctasks
import recastdb.models as dbmodels
import synctasks
import forms

from datetime import timedelta
from boto3.session import Session

from flask import Flask, redirect, jsonify, session, abort
from flask import request, url_for, render_template, flash, send_from_directory
from flask.ext import login as login
from flask.ext.api import status
from werkzeug import secure_filename
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from frontendconfig import config as frontendconf
from recastdb.database import db

log = logging.getLogger(__name__)
celeryapp  = importlib.import_module(frontendconf['RECAST_CELERYAPP']).app

ORCID_APPID = frontendconf['RECAST_ORCID_APPID']
ORCID_REDIRECT_URI = frontendconf['RECAST_ORCID_REDIRECT_URI']
ORCID_SECRET = frontendconf['RECAST_ORCID_SECRET']
ORCID_TOKEN_REDIRECT_URI = frontendconf['RECAST_ORCID_TOKEN_REDIRECT_URI']
AWS_ACCESS_KEY_ID = frontendconf['RECAST_AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = frontendconf['RECAST_AWS_SECRET_ACCESS_KEY']
DATA_FOLDER = frontendconf['RECAST_DATA_FOLDER']
AWS_S3_BUCKET_NAME = frontendconf['RECAST_AWS_S3_BUCKET_NAME']
ALLOWED_EXTENSIONS = set(['zip', 'txt'])

class User(login.UserMixin):
    def __init__(self,**kwargs):
        self.orcid = kwargs.get('orcid','no-orcid')
        self.fullname = kwargs.get('fullname','no-name')
    def get_id(self):
        return self.orcid
    def name(self):
        return self.fullname

def create_app():
    app = Flask(__name__)
    app.config.from_object(frontendconf['RECAST_FLASKCONFIG'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)
    return app

app = create_app()

login_manager = login.LoginManager()
login_manager.init_app(app)

@app.route("/")
def home():
    all_users = dbmodels.User.query.all()
    return render_template('home.html', user_data = all_users)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route('/login')
def login_user():
    if 'RECAST_DUMMYLOGIN' in frontendconf:
        user = User(orcid = frontendconf['RECAST_ORCID'], authenticated = True)
        login.login_user(user)
        return redirect(url_for('home'))

    if not request.args.has_key('code'):
        return  redirect('https://orcid.org/oauth/authorize?client_id={}&response_type=code&scope=/authenticate&redirect_uri={}&show_login=true'.format(
            ORCID_APPID,
            ORCID_REDIRECT_URI
        ))

    auth_code = request.args.get('code')
    data = {'client_id':ORCID_APPID,'client_secret':ORCID_SECRET,'grant_type':'authorization_code','code':auth_code}

    r = requests.post('https://pub.orcid.org/oauth/token', data = data)
    login_details = json.loads(r.content)

    user = User(orcid = login_details['orcid'], fullname = login_details['name'], authenticated = True)
    login.login_user(user)

    confirmUserInDB(user)
    log.warning('has email: %s',hasEmail(user))
    if not hasEmail(user):
        return redirect(url_for('signup'))

    return redirect(url_for('home'))

def confirmUserInDB(user):
    try:
        user_query = dbmodels.User.query.filter(dbmodels.User.name == user.name()).one()
        confirmOrcid(user_query)
    except MultipleResultsFound, e:
        pass
    except NoResultFound, e:
        new_user = dbmodels.User(name=user.name(), email=None, orcid_id=user.get_id())
        db.session.add(new_user)
        db.session.commit()
    return

def confirmOrcid(user_query):
    if not user_query.orcid_id:
        user_query.orcid_id = login.current_user.get_id()
        db.session.commit()

def hasEmail(user):
    try:
        user_query = dbmodels.User.query.filter(dbmodels.User.name == user.name()).one()
        if not user_query.email:
            return False
    except MultipleResultsFound, e:
        pass
    except NoResultFound, e:
        pass
    log.info('email for user %s is %s',user,user_query.email)
    return True

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = forms.SignupSubmitForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            synctasks.createSignupFromForm(app, form, login.current_user)
            flash('success! sign up has been completed', 'success')
            return redirect(url_for('home'))
    elif form.is_submitted():
        flash('failure! form did not validate and was not processed', 'danger')

    return render_template('signup.html', form=form)


@app.route("/analysis_form", methods=['GET', 'POST'])
@login.login_required
def form():
    #Analysis stuff
    myform = forms.AnalysisSubmitForm()
    run_condition_form = forms.RunConditionSubmitForm()

    collaborations = ['-None-', 'ATLAS', 'D0', 'CDF', 'CMS', 'ALEPH']
    myform.collaboration.choices = [(str(c), c) for i, c in enumerate(collaborations)]

    if myform.validate_on_submit():
        synctasks.createAnalysisFromForm(app,myform,login.current_user, run_condition_form)
        flash('success! form validated and was processed','success')
        return redirect(url_for('analyses'))

    elif myform.is_submitted():
        flash('failure! form did not validate and was not processed','danger')

    return render_template('analysis_form.html', form = myform, run_condition_form = run_condition_form)


@app.route("/userform", methods=['GET', 'POST'])
def user_form():
    userform = forms.UserSubmitForm()

    if userform.validate_on_submit():
        synctasks.createUserFromForm(app,userform)
        flash('success! form validated and was processed', 'success')
    elif userform.is_submitted():
        flash('failure! form did not validate and was not processed', 'danger')

    return render_template('form.html', form=userform)

@app.route("/editsubscription", methods=['GET', 'POST'], defaults={'id':0})
@app.route("/editsubscription/<int:id>", methods=['GET', 'POST'])
def edit_subscription(id):
    pass

@app.route("/editanalysis", methods=['GET', 'POST'], defaults={'id':0})
@app.route("/editanalysis/<int:id>", methods=['GET', 'POST'])
def edit_analysis(id):
    pass


@app.route("/editrequest", methods=['GET', 'POST'], defaults={'id':0})
@app.route("/editrequest/<int:id>", methods=['GET', 'POST'])
def edit_request(id):
    pass

@app.route("/request_form", methods=['GET','POST'], defaults={'id': 1})
@app.route('/request_form/<int:id>', methods=['GET', 'POST'])
@login.login_required
def request_form(id):
    request_form = forms.RequestSubmitForm()

    analysis = db.session.query(dbmodels.Analysis).filter(dbmodels.Analysis.id == id).all()
    request_form.analysis_id.data = analysis[0].id

    if request.method == 'POST':
        if request_form.validate_on_submit():
            request_uuid = str(uuid.uuid4())
            request_form.uuid.data = request_uuid
            request_id = synctasks.createRequest(app,request_form,login.current_user)
            flash('success!', 'success')
            return redirect(url_for('analyses'))

        elif request_form.is_submitted():
            print request_form.errors
            flash('failure! form did not validate and was not processed','danger')

    return render_template('request_form.html', form=request_form, analysis = analysis[0])


@app.route("/subscribe", methods=('GET', 'POST'), defaults={'id': 1})
@app.route('/subscribe/<int:id>')
@login.login_required
def subscribe(id):
    subscribe_form = forms.SubscribeSubmitForm()
    analysis = db.session.query(dbmodels.Analysis).filter(dbmodels.Analysis.id == id).all()
    subscribe_form.analysis_id.data = analysis[0].id

    if subscribe_form.validate_on_submit():
        synctasks.createSubscriptionFromForm(app, subscribe_form, login.current_user)
        flash('success! You have been subscribed', 'success')
        return redirect(url_for('analyses'))
    elif subscribe_form.is_submitted():
        flash('failure!', 'failure')

    return render_template('subscribe.html', form=subscribe_form, analysis = analysis[0])

@app.route("/contact", methods=('GET', 'POST'), defaults={'id': 1})
@app.route('/contact/<int:id>')
@login.login_required
def contact(id):
    contact_form = forms.ContactSubmitForm()
    user = db.session.query(dbmodels.User).filter(dbmodels.User.name == login.current_user.name()).all()
    contact_form.responder.data = user[0].name
    contact_form.responder_email.data = user[0].email

    return render_template('contact.html', form = contact_form)

# Views
@app.route('/analyses', methods=['GET', 'POST'], defaults={'id': None})
@app.route('/analyses/<int:id>', methods=['GET', 'POST'])
def analyses(id):
    if id:
        query = db.session.query(dbmodels.Analysis).filter(
          dbmodels.Analysis.id == id
        ).all()
        return render_template('analysis.html', analysis=query[0])
    else:
        if request.args.has_key('sort'):
            query  = db.session.query(dbmodels.Analysis).order_by(dbmodels.Analysis.title).all()
            return render_template('analyses_views.html', analyses = query)

        if request.args.has_key('max_results'):
            pass
    query = db.session.query(dbmodels.Analysis).all()
    return render_template('analyses_views.html', analyses = query)

@app.route('/requests', methods=['GET', 'POST'], defaults={'id': None})
@app.route('/requests/<int:id>', methods=['GET', 'POST'])
@login.login_required
def request_views(id):
    if id:
        query = db.session.query(dbmodels.ScanRequest).filter(
            dbmodels.ScanRequest.id == id).all()
        return render_template('request.html',
                                request=query[0],
                                bucket_name=AWS_S3_BUCKET_NAME)
    else:
        if request.args.has_key('sort'):
            query = db.session.query(dbmodels.ScanRequest).order_by(dbmodels.ScanRequest.title).all()
            return render_template('request_views.html', requests = query)

        query = db.session.query(dbmodels.ScanRequest).all()
        return render_template('request_views.html', requests = query)


@app.route('/subscriptions')
@login.login_required
def subscriptions():
    query = db.session.query(dbmodels.Subscription).all()
    return render_template('subscriptions.html', subscriptions = query)


@app.route("/users")
@login.login_required
def users():
    query = db.session.query(dbmodels.User).all()
    users = rows_to_dict(query)
    return render_template('viewer.html', rows = users, title= dbmodels.User.__table__)


@app.route("/links")
@login.login_required
def display_links():
    return render_template('links.html')

@app.route("/userstories")
@login.login_required
def display_user_stories():
    return render_template('userstories.html')

@app.route("/testing", defaults={'page': 1})
@app.route('/testing/page/<int:page>')
@login.login_required
def display_testing(page):
    query = db.session.query(dbmodels.Analysis).all()
    count = len(query)
    new_query = get_elements_for_page(page, 5, count, query)

    if not new_query and page != 1:
        pass
    return render_template('testing.html', analyses = new_query)

@app.route("/list-subscriptions-for-analysis", defaults={'analysis_id': 1})
@app.route("/list-subscriptions-for-analysis/<int:analysis_id>")
@login.login_required
def list_subscriptions(analysis_id):
    query = db.session.query(dbmodels.Subscription).filter(dbmodels.Subscription.analysis_id == analysis_id).all()
    return render_template('list_subscriptions.html', subscriptions = query)

@app.route("/list-requests-for-analysis", defaults={'analysis_id': 1})
@app.route("/list-requests-for-analysis/<int:analysis_id>")
@login.login_required
def list_requests(analysis_id):
    query = db.session.query(dbmodels.ScanRequest).filter(dbmodels.ScanRequest.analysis_id == analysis_id).all()
    return render_template('request_views.html', requests = query)

def get_elements_for_page(page, PER_PAGE, count, obj):
    first_index = (page - 1) * PER_PAGE
    last_index = first_index + PER_PAGE
    return obj[first_index:last_index]


def url_for_other_page(page):
    args = request.view_args.copy
    args['page'] = page
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_pages'] = url_for_other_page

# Other functions ---------------------------------------------------------------------------

@app.route("/logout")
@login.login_required
def logout():
    login.logout_user()
    return redirect('/')

@login_manager.user_loader
def load_user(userid):
    r = requests.get('http://pub.orcid.org/v1.2/{}/orcid-profile'.format(userid), headers = {'Accept':'application/json'})
    login_bio = json.loads(r.content)['orcid-profile']['orcid-bio']
    return User(orcid = userid, fullname = '{} {}'.format(login_bio['personal-details']['given-names']['value'],login_bio['personal-details']['family-name']['value']))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login_user'))

@app.route("/profile", methods=['GET', 'POST'])
@login.login_required
def profile():
    user_query = dbmodels.User.query.filter(dbmodels.User.name == login.current_user.name()).all()
    assert len(user_query)

    if request.method == 'POST':
        token = dbmodels.AccessToken.query.filter(dbmodels.AccessToken.id == request.form['delete']).one()
        db.session.delete(token)
        db.session.commit()

    return render_template('profile.html', db_user = user_query[0], tokens=user_query[0].access_tokens)

@app.route("/token", methods=['GET', 'POST'])
@login.login_required
def show_token():
    user_query = dbmodels.User.query.filter(dbmodels.User.name == login.current_user.name()).all()
    assert len(user_query)

    if request.method == 'POST':
        new_token = dbmodels.AccessToken(token_name=request.form['tokenname'], user_id=user_query[0].id)
        db.session.add(new_token)
        db.session.commit()
    elif request.method == 'GET':
        tokens = db.session.query(dbmodels.AccessToken).all()
        new_token = tokens[len(tokens)-1]

    if not request.args.has_key('code'):
        return  redirect('https://orcid.org/oauth/authorize?client_id={}&response_type=code&scope=/authenticate&redirect_uri={}&show_login=true'.format(
                    ORCID_APPID,
                    ORCID_TOKEN_REDIRECT_URI
                ))

    auth_code = request.args.get('code')
    data = {'client_id':ORCID_APPID,'client_secret':ORCID_SECRET,'grant_type':'authorization_code','code':auth_code, 'redirect_uri':ORCID_TOKEN_REDIRECT_URI}

    r = requests.post('https://pub.orcid.org/oauth/token', data = data)
    login_details = json.loads(r.content)


    if not user_query[0].orcid_id:
        user_query[0].orcid_id = login_details['orcid']
        db.session.add(user_query[0])
        db.session.commit()

    new_token.token = login_details['access_token']
    db.session.add(new_token)
    db.session.commit()
    return render_template('new_token.html', token=new_token, user=user_query[0])

@app.route("/search", methods=['GET', 'POST', 'PUT'])
def search():
    q = request.args.get('q')

    if request.method == 'POST':
        q = request.form['q']
        doc_type = None
        print request.form['filter']
        if request.form['filter'] == 'Analysis':
            doc_type = 'analysis'
            search_data = synctasks.search(ELASTIC_SEARCH_URL,
                                           ELASTIC_SEARCH_AUTH,
                                           ELASTIC_SEARCH_INDEX,
                                           doc_type,
                                           q)
            ids = []
            for entry in search_data['hits']['hits']:
                ids.append(entry['_source']['id'])

            ids.sort()
            query = db.session.query(dbmodels.Analysis).filter(dbmodels.Analysis.id.in_(ids)).all()
            return render_template('analyses_views.html', analyses = query)

        elif request.form['filter'] == 'Request':
            doc_type = 'requests'
            search_data = synctasks.search(ELASTIC_SEARCH_URL,
                                           ELASTIC_SEARCH_AUTH,
                                           ELASTIC_SEARCH_INDEX,
                                           doc_type,
                                           q)

            ids = []
            for entry in search_data['hits']['hits']:
                ids.append(entry['_source']['id'])

            ids.sort()
            query = db.session.query(dbmodels.ScanRequest).filter(dbmodels.ScanRequest.id.in_(ids)).all()
            print len(query)
            return render_template('request_views.html', requests = query)

    return render_template('search.html', search_data=json.dumps(search_data['hits']['hits']))

def rows_to_dict(rows):
    d = []
    for row in rows:
        new_dict = {}
        for column in row.__table__.columns:
            new_dict[column.name] = getattr(row, column.name)
        d.append(new_dict)
    return d

@app.route("/arxiv", methods=['GET', 'POST'])
def arxiv():
    if request.args.has_key('id'):
        arxiv_id = request.args.get('id')
    else:
        #No id found return an error
        return
    print arxiv_id
    fields = "title,author,doi,abstract,corporate_name"
    url = "https://inspirehep.net/search?p={}&of=recjson&ot={}".format(arxiv_id,fields)
    print url
    response = requests.get(url)

    if not response.content or len(response.json()) > 1 or len(response.json()) == 0:
        """No record found"""
        return
    if len(response.json()) > 1:
        """More than one record found"""
        return

    result = response.json()[0]

    data = {}
    data['title'] = result['title']['title'] or None
    data['collaboration'] = result['corporate_name'][0]['collaboration'] or None
    data['doi'] = result['doi'][0] or None
    data['description'] = result['abstract'][1]['summary']
    return jsonify(data)

@app.route("/add-parameter/<int:request_id>", methods=['GET', 'POST'])
@login.login_required
def add_parameter_point(request_id):
    request_query = db.session.query(dbmodels.ScanRequest).filter(dbmodels.ScanRequest.id == request_id).one()
    point_request_id = synctasks.createPointRequest(app,
                                                    request_id,
                                                    login.current_user)
    for k in request.form:
        coordinate = json.loads(request.form[k])

        if coordinate.has_key('value'):
            value = coordinate['value']
            name = None
        if coordinate.has_key('name'):
	       name = coordinate['name']

    	synctasks.createPointCoordinate(app,
                                        login.current_user,
                                        name,
                                        float(value),
                                        point_request_id)
    response = {}
    response['success'] = True
    return jsonify(response)


@app.route("/add-basic-request/<int:point_request_id>", methods=['POST'])
@login.login_required
def add_basic_request(point_request_id):
    point_request_query = db.session.query(dbmodels.PointRequest).filter(
                                dbmodels.PointRequest.id == point_request_id
                            ).one()

    request_query = db.session.query(dbmodels.ScanRequest).filter(
                        dbmodels.ScanRequest.id == point_request_query.scan_request_id
                    ).one()

    if request.files['file']:
        zip_file = request.files['file']

        file_uuid = str(uuid.uuid4())
        zip_file.save(zip_file.filename)

        synctasks.createBasicRequestWithArchive(
            app, login.current_user, point_request_id, file_uuid, zip_file.filename
        )
        synctasks.uploadToAWS(AWS_ACCESS_KEY_ID,
                              AWS_SECRET_ACCESS_KEY,
                              AWS_S3_BUCKET_NAME,
                              zip_file,
                              file_uuid)

        response = {}
        response['success'] = True
        return jsonify(response)
    else:
        return

@app.route("/add-coordinate", methods=['GET', 'POST'])
@app.route("/add-coordinate/<int:point_request_id>", methods=['GET', 'POST'])
def add_coordinate(point_request_id):

    if request.method == 'POST':

        point_request_query = db.session.query(dbmodels.PointRequest).filter(
                                  dbmodels.PointRequest.id == point_request_id
                                ).one()

        data = json.loads(request.data.decode())
        coordinate = data['value']
        coordinate_name = data['name']
        point_coordinate_id = synctasks.createPointCoordinate(app,
                                                              login.current_user,
                                                              coordinate_name,
                                                              coordinate,
                                                              point_request_query.id)
    return ""

@app.route("/homestats")
def homestats():
    analyses = db.session.query(dbmodels.Analysis).all()
    requests = db.session.query(dbmodels.ScanRequest).all()

    data = {}
    data['analyses'] = len(analyses)
    data['requests'] = len(requests)
    return jsonify(data)

@app.route("/parameter-data/<int:id>")
def parameter_data(id):
    try:
        query = db.session.query(dbmodels.PointRequest).filter(
                    dbmodels.PointRequest.id == id
                ).one()
        response = {}
        response['data'] = render_template('parameter_data.html',
                                       pointrequest=query,
                                       bucket_name=AWS_S3_BUCKET_NAME)
        response['success'] = "true"
        return jsonify(response)

    except MultipleResultsFound, e:
        #return 'Multiple choices found', status.HTTP_300_MULTIPLE_CHOICES
        return abort(500)

    except NoResultFound, e:
        #return 'No result found', status.HTTP_404_NOT_FOUND
        return abort(500)

@app.route("/point-response-data/<int:id>")
def point_response_data(id):
    try:
        query = db.session.query(dbmodels.PointResponse).filter(
                    dbmodels.PointResponse.id == id
                ).one()

        response = {}
        response['data'] = render_template('response_data.html',
                                       pointresponse=query,
                                       bucket_name=AWS_S3_BUCKET_NAME)
        response['success'] = "true"
        return jsonify(response)

    except MultipleResultsFound, e:
        #return 'Multiple choices found', status.HTTP_300_MULTIPLE_CHOICES
        return abort(500)


    except NoResultFound, e:
        #return 'No result found', status.HTTP_404_NOT_FOUND
        return abort(500)

@app.route("/basic-response-data/<int:id>")
def basic_response_data(id):
    try:
        query = db.session.query(dbmodels.BasicResponse).filter(
      dbmodels.BasicResponse.id == id).one()

        response = {}
        response['data'] = render_template('basic_response_data.html',
                                            basicresponse=query,
                                            bucket_name=AWS_S3_BUCKET_NAME)
        response['success'] = "true"
        return jsonify(response)

    except MultipleResultsFound, e:
        #return 'Multiple choices dound', status.HTTP_300_MULTIPLE_CHOICES
        return abort(500)

    except NoResultFound, e:
        #return 'No result found', status.HTTP_404_NOT_FOUND
        return abort(500)


@app.route('/download/response/<int:id>/json')
def download_response_json(id):
    try:
        query = db.session.query(dbmodels.PointResponse).filter(
      dbmodels.PointResponse.id == id).one()
        query_json = synctasks.to_dict(query)

        if not os.path.isdir(DATA_FOLDER):
            # check if data folder exist else create one
            try:
                os.makedirs(DATA_FOLDER)
            except Exception, e:
                abort(500)

        name = str(uuid.uuid1())
        filename = '{}/{}.json'.format(DATA_FOLDER, name)
        target = open(filename, 'w')
        target.write(yaml.dump(query_json, default_style=False))
        target.close()
        return send_from_directory(directory=os.getcwd(), filename=filename)
    except MultipleResultsFound, e:
        return abort(500)
    except NoResultFound, e:
        return abort(500)

@app.route('/download/basic-response/<int:id>/json')
def download_basic_response_json(id):
    try:
        query = db.session.query(dbmodels.BasicResponse).filter(
          dbmodels.BasicResponse.id == id
        ).one()
        query_json = synctasks.to_dict(query)

        if not os.path.isdir(DATA_FOLDER):
           # check if data folder exist
            try:
                os.makedirs(DATA_FOLDER)
            except Exception, e:
                # abort, server error
                abort(500)
        name = str(uuid.uuid1())
        filename = '{}/{}.json'.format(DATA_FOLDER, name)
        target = open(filename, 'w')
        target.write(yaml.dump(query_json, default_style=False))
        target.close()

        return send_from_directory(directory=os.getcwd(), filename=filename)

    except MultipleResultsFound, e:
        return abort(500)
    except NoResultFound, e:
        return abort(500)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/search-results")
def search_results():
    return render_template('search-results.html', search_term=request.args.get('search'))

@app.route("/search-ajax")
def search_ajax():
    pass

@app.route("/search-analyses/<string:query>")
def search_analyses(query):
    doc_type = 'analysis'
    results = synctasks.search(ELASTIC_SEARCH_URL,
                             ELASTIC_SEARCH_AUTH,
                             ELASTIC_SEARCH_INDEX,
                             doc_type,
                             query)
    ids = []

    for entry in search_data['hits']['hits']:
        ids.append(entry['_source']['id'])

    ids.sort()
    analyses = db.session.query(dbmodels.Analysis).filter(
        dbmodels.Analysis.id.in_(ids)
    ).all()

    response = {}
    response['data'] = render_template('analysis-search-results.html', query=analyses)
    response['success'] = True

    return jsonify(response)

@app.route("/search-results/<string:query>")
def search_requests(query):
    doc_type = 'requests'
    results = synctasks.search(ELASTIC_SEARCH_URL,
                             ELASTIC_SEARCH_AUTH,
                             ELASTIC_SEARCH_INDEX,
                             doc_type,
                             query)
    ids = []

    for entry in search_data['hits']['hits']:
        ids.append(entry['_source']['id'])

    ids.sort()
    request_results = db.session.query(dbmodels.ScanRequest).filter(
        dbmodels.ScanRequest.id.in_(ids)
    ).all()

    response = {}
    response['data'] = render_template('request-search_results.html', query=request_results)
    response['success'] = True

    return jsonify(response)

@app.route('/stored_file/<path:path>')
def static_proxy(path):
    import boto3
    from flask import Response
    s3 = boto3.Session(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY).resource('s3')
    obj = s3.Object(AWS_S3_BUCKET_NAME,path)
    response = obj.get()
    return Response(response['Body'].read(), headers=response['ResponseMetadata']['HTTPHeaders'])
