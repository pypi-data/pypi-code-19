from celery import shared_task, task

@shared_task
def hello_world():
    print "hello world"
    print "*"*200

@shared_task
def upload_to_zenodo(current_user, ORCID, reason_for_request, lhe_file):
    url = "https://zenodo.org/api/deposit/depositions/?access_token={}".format(ZENODO_ACCESS_TOKEN)

    import uuid
    request_uuid = uuid.uuid1()
    description = "RECAST_request: {} \n Requester: {}, ORCID: {} \n Request_description: {}".format(
                        request_uuid,
                        current_user.name(),
                        current_user.orcid,
                        reason_for_request
                    )

    deposition_data = {
                        "metadata":{
                            "access_right": "embargoed",
                            "upload_type": "dataset",
                            "creators": [{"name": "Bora, Christian"}],
                            "description": description,
                            "title": "Sample title"
                        }
                    }

    deposition_response = requests.post(url, json.dumps(deposition_data), headers=headers)
    deposition_id = deposition_response.json['id']

    url_deposition_file = "https://zenodo.org/api/deposit/depositions/{}/files?access_token={}".format(deposition_id, ZENODO_ACCESS_TOKEN)

    deposition_file_data = {"filename": lhe_file.filename}
    files = {"file": open(secure_filename(lhe_file.filename), 'rb')}

    deposition_file_response = requests.post(url_deposition_file, data=deposition_file_data, files=files)
