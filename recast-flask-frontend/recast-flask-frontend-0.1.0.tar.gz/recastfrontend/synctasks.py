import datetime
import requests
import json
import recastdb.models as dbmodels
from recastdb.database import db
from boto3.session import Session
from werkzeug import secure_filename
from elasticsearch import Elasticsearch

def createAnalysisFromForm(app,form,current_user, run_condition_form):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query)==1
        run_condition = dbmodels.RunCondition(
                                    name = run_condition_form.name.data,
                                    description = run_condition_form.description.data
                                )

        db.session.add(run_condition)
        db.session.commit()

        analysis = dbmodels.Analysis(
                                owner_id = user_query[0].id,
                                title = form.title.data,
                                collaboration = form.collaboration.data,
                                arxiv_id = form.arxiv_id.data,
                                doi = form.doi.data,
                                inspire_id = form.inpire_id.data,
                                cds_id = form.cds_id.data,
                                description = form.description.data,
                                run_condition_id = run_condition.id
                                )

        db.session.add(analysis)
        db.session.commit()


def createUserFromForm(app, form):
    with app.app_context():
        user = dbmodels.User(name = form.name.data, email = form.email.data)

        db.session.add(user)
        db.session.commit()

def createModelFromForm(app, form, current_user):
    with app.app_context():

        model = dbmodels.Model(form.model_description.data)
        db.session.add(model)
        db.session.commit()

def createRunConditionFromForm(app, form, current_user):
    with app.app_context():
        run_condition = dbmodels.RunCondition(
                    name = form.name.data,
                    description = form.description.data
                    )

        db.session.add(run_condition)
        db.session.commit()


# Request tables --------------------------------------------------------------------------
def createRequest(app, request_form, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query)==1

        scan_request = dbmodels.ScanRequest(
          requester_id = user_query[0].id,
          title = request_form.title.data,
          reason_for_request = request_form.reason_for_request.data,
          additional_information = request_form.additional_information.data,
          analysis_id = request_form.analysis_id.data,
          post_date = datetime.date.today()
        )
        db.session.add(scan_request)
        db.session.commit()
        return scan_request.id

def createPointRequest(app, request_id, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query) == 1

        point_request = dbmodels.PointRequest(
          requester_id = user_query[0].id,
          scan_request_id = request_id
          )
        db.session.add(point_request)
        db.session.commit()

        return point_request.id

def createBasicRequestWithArchive(app, current_user, PR_id, file_name, original_name):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query) == 1

        basic_request = dbmodels.BasicRequest(
          requester_id = user_query[0].id,
          point_request_id = PR_id
        )
        db.session.add(basic_request)
        db.session.commit()

        zip_file = dbmodels.RequestArchive(
          file_name = file_name,
          path = './',
          zenodo_file_id = None,
          original_file_name = original_name,
          basic_request_id = basic_request.id
        )
        db.session.add(zip_file)
        db.session.commit()
        return zip_file.id

def createPointCoordinate(app, current_user, name, value, PR_id):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query) ==1

        point_coordinate = dbmodels.PointCoordinate(value = value,
                                                point_request_id = PR_id,
                                                title = name)
        db.session.add(point_coordinate)
        db.session.commit()

        return point_coordinate.id


def createRequestFromForm(app, request_form, current_user, parameter_points):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query)==1

        scan_request = dbmodels.ScanRequest(
          requester_id = user_query[0].id,
          title = request_form.title.data,
          reason_for_request = request_form.reason_for_request.data,
          additional_information = request_form.additional_information.data,
          analysis_id = request_form.analysis_id.data,
          zenodo_deposition_id = request_form.zenodo_deposition_id.data,
          uuid = request_form.uuid.data,
          post_date = datetime.date.today()
          )

        db.session.add(scan_request)
        db.session.commit()

        for parameter in parameter_points:
            point_request = dbmodels.PointRequest(requester_id = user_query[0].id,
                                          scan_request_id = scan_request.id
                                          )

            db.session.add(point_request)
            db.session.commit()

            parameter_point = dbmodels.PointCoordinate(
                value = parameter.parameter_point.data,
                point_request_id = point_request.id
            )

            db.session.add(parameter_point)
            db.session.commit()

            basic_request = dbmodels.BasicRequest(requester_id = user_query[0].id,
                                                  point_request_id = point_request.id
                                          )

            db.session.add(basic_request)
            db.session.commit()

            zip_file = dbmodels.RequestArchive(
                file_name = parameter.uuid.data,
                path = './',
                zenodo_file_id = parameter.zenodo_file_id.data,
                original_file_name = parameter.zip_file.data.filename,
                basic_request_id = basic_request.id
            )
            db.session.add(zip_file)
            db.session.commit()

def createScanRequestFromForm(app, form, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query)==1

        request = dbmodels.ScanRequest(requester_id = int(form.requester_choice.data),
                                   model_id = int(form.model_choice.data),
                                   analysis_id = int(form.analysis_choice.data),
                                   description_of_model = form.description_of_model.data
                                   )

        db.session.add(request)
        db.session.commit()


def createPointRequestFromForm(app, form, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()

        assert len(user_query) == 1

        point_request = dbmodels.PointRequest(model_id = int(form.model_choice.data),
                                          scan_request_id = int(form.scan_request_choice.data),
                                          requester_id = user_query[0].id
                                          )

        db.session.add(point_request)
        db.session.commit()


def createBasicRequestFromForm(app, form, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query) == 1

        basic_request = dbmodels.BasicRequest(conditions_description = form.conditions_description.data,
                                          requester_id = user_query[0].id
                                          )
        db.session.add(basic_request)
        db.session.commit()


def createSubscriptionFromForm(app, form, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query) == 1

        subscription = dbmodels.Subscription(subscription_type = form.subscription_type.data,
                                          description = form.description.data,
                                          requirements = form.requirements.data,
                                          notifications = '\n'.join(form.notifications.data),
                                          subscriber_id = user_query[0].id,
                                          analysis_id = form.analysis_id.data
                                          )
        db.session.add(subscription)
        db.session.commit()

def createSignupFromForm(app, form, current_user):
    with app.app_context():
        user_query = dbmodels.User.query.filter(dbmodels.User.name == current_user.name()).all()
        assert len(user_query) == 1

        user_query[0].email = form.email.data
        db.session.commit()

def uploadToAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, zip_file, file_uuid):
    session = Session(AWS_ACCESS_KEY_ID,
                    AWS_SECRET_ACCESS_KEY)
    s3 = session.resource('s3')
    data = open(secure_filename(zip_file.filename), 'rb')
    s3.Bucket(AWS_S3_BUCKET_NAME).put_object(Key=str(file_uuid), Body=data, ACL='public-read')

def downloadFromAWS(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME, file_uuid, original_file_name):

    session = Session(AWS_ACCESS_KEY_ID,
                      AWS_SECRET_ACCESS_KEY)

    s3 = session.resource('s3')
    s3.Bucket(AWS_S3_BUCKET_NAME).download(Key=str(file_uuid), Filename=original_file_name)

def createDeposition(ZENODO_ACCESS_TOKEN, request_uuid, current_user, description, request_title):
    url = "https://zenodo.org/api/deposit/depositions/?access_token={}".format(ZENODO_ACCESS_TOKEN)
    headers = {"Content-Type": "application/json"}
    description = "RECAST_request: {} Requester: {} ORCID: {} Request_title: {} Request_description: {}".format(
        request_uuid,
        current_user.name(),
        current_user.get_id(),
        request_title,
        description
    )

    deposition_data = {
        "metadata": {
            "access_right": "embargoed",
            "upload_type": "dataset",
            "creators": [{"name": "Bora, Christian"}],
            "description": description,
            "title": request_title
        }
    }
    response = requests.post(url, data=json.dumps(deposition_data), headers=headers)
    if response.ok:
	   deposition_id = response.json()['id']
    else:
	   print "Failed to create a deposition on Zenodo"
	   deposition_id = -1
    return deposition_id

def uploadToZenodo(ZENODO_ACCESS_TOKEN, deposition_id, file_uuid, zip_file):
    url = "https://zenodo.org/api/deposit/depositions/{}/files?access_token={}".format(
            deposition_id,
            ZENODO_ACCESS_TOKEN)
    json_data_file = {"filename": file_uuid}
    files = {'file': open(secure_filename(zip_file.filename), 'rb')}
    response_file = requests.post(url,
								data=json_data_file,
								files=files)
    print response_file.status_code
    if response_file.ok:
	   deposition_file_id = response_file.json()['id']
    else:
	   print "Failed to upload file to Zenodo"
	   deposition_file_id = -1
    return deposition_file_id

def publish(ZENODO_ACCESS_TOKEN, deposition_id):
    url = "https://zenodo.org/api/deposit/depositions/{}/actions/publish?access_token={}".format(
        deposition_id,
        ZENODO_ACCESS_TOKEN)
    response = requests.post(url)

def search(ES_HOST_NAME, ES_AUTH, ES_INDEX, doc_type, query_string):
    """ Search function with ElasticSearch backend

    :param ES_HOST_NAME: elasticsearch link
    :param ES_AUTH: username and password of elasticsearch
    :param ES_INDEX: index of where to search
    :param doc_type: request or analysis
    :param query_string: string to search
    """

    es = Elasticsearch([{'host': ES_HOST_NAME,
                       'port': 443,
                       'use_ssl': True,
                       'http_auth': ES_AUTH}])
    response = es.search(index=ES_INDEX, doc_type=doc_type, body={
      "query": {
        "filtered": {
          "query": {
            "query_string": {
              "query": query_string
              }
            }
          }
        }
      })

    return response


def to_dict(query, query_instance=None):
    """ Function to encode SQLAlchemy object to json

    :param query: alchemy result query object
    :param query_instance:
    """

    if hasattr(query, '__table__'):
        return {c.name: str(getattr(query, c.name)) for c in query.__table__.columns}
    else:
        cols = query_instance.column_descriptions
        return { cols[i]['name'] : query[i] for i in range(len(cols)) }
