import sys
import tempfile
import os
import shlex
import subprocess
import json
import time
aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1', 'eu-west-1', 'eu-central-1',
               'eu-west-2', 'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-2', 'ap-south-1', 'sa-east-1']


def parse_image_json(text):
    """
    parses response output of AWS describe commands and returns the first (and only) item in array
    :param text: describe output
    :return: image json
    """
    image_details = json.loads(text)
    if image_details.get('Images') is not None:
        try:
            image_details = image_details.get('Images')[0]
        except IndexError:
            image_details = None
    return image_details


class AWSUtils:
    """ Methods necessary to perform VM imports """

    def __init__(self, config_save_dir, aws_profile, bucket, regions, ami_name, upload_file):
        """
        Instantiate with common properties for all VM imports to AWS
        :param config_save_dir: where to save aws config files
        :param aws_project: which aws_project to upload to
        :param profile: which aws credential profile to use
        :param region: which aws region to impot AMI into
        """
        self.aws_project = aws_profile
        self.aws_regions = regions
        self.config_save_dir = config_save_dir
        self.bucket_name = bucket
        self.ami_name = ami_name
        self.upload_file = upload_file

    def validate(self):
        """
        Call instance validation methods
        :return:
        """
        self.validate_regions()
        self.validate_bucket()
        self.validate_ec2_action()

    def validate_regions(self):
        """
        Validate the user specified regions are valid
        :return:
        """
        for region in self.aws_regions:
            if region not in aws_regions:
                print "Error: Specified region: {} is not a valid aws_region".format(region)
                print "Valid regions are: {}".format(aws_regions)

    def validate_ec2_action(self):
        """
        Attempt to validate that the provided user has permissions to import an AMI
        :return:
        """
        import_cmd = 'aws ec2 import-image --dry-run --profile {} --region {}'\
            .format(self.aws_project, self.aws_regions[0])
        print "Attempting ec2 import dry run: {}".format(import_cmd)
        try:
            subprocess.check_output(shlex.split(import_cmd), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "(DryRunOperation)" in e.output:
                # If it failed because of a dry run (what we asked for) then this except can be ignored
                print "Dry run operation successful!"
                return
            print "Error: {}".format(e.output)
            print "It doesn't seem like your user has the required permissions to import an ami image from s3"
            sys.exit(5)

    def validate_bucket(self):
        """
        Do a quick check to see if the s3 bucket is valid
        :return:
        """
        s3_check_cmd = "aws s3 ls s3://{} --profile '{}' --region '{}'".format(self.bucket_name, self.aws_project,
                                                                               self.aws_regions[0])
        print "Checking for s3 bucket"
        try:
            subprocess.check_output(shlex.split(s3_check_cmd))
        except subprocess.CalledProcessError as e:
            print "Error: {}".format(e)
            print "Unable to query s3 bucket: {}. Validate that it exists, and your user has sufficient permissions"\
                .format(self.bucket_name)
            sys.exit(5)

    def get_image_id_by_name(self, ami_name, region='us-east-1'):
        """
        Locate an AMI image id by name in a particular region
        :param ami_name: ami name you need the id for
        :param region: the region the image exists in
        :return: id of the image
        """
        image_details = None
        detail_query_attempts = 0

        while image_details is None:
            describe_cmd = "aws ec2 describe-images --filters 'Name=name,Values={}' --profile '{}' --region {}"\
                .format(ami_name, self.aws_project, region)
            res = subprocess.check_output(shlex.split(describe_cmd))

            print "describe command returned: {}".format(res)

            image_details = parse_image_json(res)
            if not image_details:
                if detail_query_attempts > 5:
                    print "Tried to get image details 5 times and failed, exiting"
                    raise Exception("Unable to get AMI image id from AWS using the image name")
                time.sleep(10)
                print "No images defined returned yet, will try another query"
                detail_query_attempts += 1

        image_id = image_details['ImageId']
        print "located image id: {}".format(image_id)
        return image_id

    def copy_ami_to_new_name(self, ami_id, new_name, source_region='us-east-1'):
        """
        Copies an AMI from the default region and name to the desired name and region
        :param ami_id: ami id to copy
        :param new_name: name of the new ami to create
        :param source_region: the source region of the ami to copy
        """

        new_image_ids = []

        for region in self.aws_regions:
            copy_img_cmd = "aws ec2 copy-image --source-image-id {} --profile {} --source-region {} --region {} --name {}"\
                .format(ami_id, self.aws_project, source_region, region, new_name)
            res = subprocess.check_output(shlex.split(copy_img_cmd))

            print "Copy cmd returned: {}".format(res)

            new_image_id = json.loads(res).get('ImageId')
            new_image_ids.append((new_image_id, region))

            print "new image Id is: {}".format(new_image_id)

        print "monitoring the copies for the following regions/id : {}".format(new_image_ids)
        for tupp in new_image_ids:
            image_id = tupp[0]
            image_region = tupp[1]
            self.wait_for_copy_available(image_id, image_region)

    def deregister_image(self, ami_id, region='us-east-1'):
        """
        Deregister an AMI by id
        :param ami_id:
        :param region: region to deregister from
        :return:
        """
        deregister_cmd = "aws ec2 --profile {} --region {} deregister-image --image-id {}"\
            .format(self.aws_project, region, ami_id)
        print "De-registering old image, now that the new one exists."
        print "De-registering cmd: {}".format(deregister_cmd)
        res = subprocess.check_output(shlex.split(deregister_cmd))
        print "Response: {}".format(res)
        print "Not monitoring de-register command"

    def wait_for_copy_available(self, image_id, region):
        """
        Wait for the newly copied ami to become available
        :param image_id: image id to monitor
        :param region: region to monitor copy
        """
        waiting = True

        describe_image_cmd = "aws ec2 --profile {} --region {} --output json describe-images --image-id {}"\
            .format(self.aws_project, region, image_id)
        while waiting:
            res = subprocess.check_output(shlex.split(describe_image_cmd))
            print "described image returned: {}".format(res)
            image_json = parse_image_json(res)
            image_state = image_json['State']
            if image_state == 'available':
                print "Copied AMI is renamed and ready to use!"
                return
            elif image_state == 'failed':
                print "Copied AMI failed for some reason..."
                sys.exit(5)
            else:
                print "image state is currently: {}".format(image_state)
                print "Sleeping for 30 seconds..."
                time.sleep(30)

    def rename_image(self, ami_name, new_ami_name, source_region='us-east-1'):
        """
        Method which renames an ami by copying to a new ami with a new name (only way this is possible in AWS)
        :param ami_name:
        :param new_ami_name:
        :return:
        """
        print "Re-naming/moving AMI to desired name and region"
        image_id = self.get_image_id_by_name(ami_name, source_region)
        self.copy_ami_to_new_name(image_id, new_ami_name, source_region)
        self.deregister_image(image_id, source_region)

    def create_config_file(self, vmdk_location, description):
        """
        Create the aws import config file
        :param vmdk_location: location of downloaded VMDK
        :param description: description to use for config_file creation
        :return: config file descriptor, config file full path
        """
        description = description
        format = "vmdk"
        user_bucket = {
            "S3Bucket": self.bucket_name,
            "S3Key": vmdk_location
        }
        parent_obj = {'Description': description, 'Format': format, 'UserBucket': user_bucket}
        obj_list = [parent_obj]

        temp_fd, temp_file = tempfile.mkstemp()
        print 'creating tmp file for {} at {}'.format(vmdk_location, temp_file)

        with os.fdopen(temp_fd, 'w') as f:
            json.dump(obj_list, f)
        return temp_fd, temp_file

    def run_ec2_import(self, config_file_location, description, region='us-east-1'):
        """
        Runs the command to import an uploaded vmdk to aws ec2
        :param config_file_location: config file of import param location
        :param description: description to attach to the import task
        :return: the import task id for the given ami
        """
        import_cmd = "aws ec2 import-image --description '{}' --profile '{}' --region '{}' --output 'json'" \
                     " --disk-containers file://{}"\
            .format(description, self.aws_project, region, config_file_location)
        try:
            res = subprocess.check_output(shlex.split(import_cmd), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print "Error importing to ec2"
            print "output: {}".format(e.output)
            sys.exit(5)

        print "got res: {}".format(res)
        res_json = json.loads(res)
        task_running, import_id = self.check_task_status_and_id(res_json)
        return import_id

    def upload_to_s3(self, region='us-east-1'):
        """
        Uploads the vmdk file to aws s3
        :param file_location: location of vmdk
        :return:
        """
        s3_import_cmd = "aws s3 cp {} s3://{} --profile '{}' --region {}".format(self.upload_file, self.bucket_name,
                                                                                 self.aws_project, region)
        print "Uploading to bucket {} in s3 with the cmd: {}".format(self.bucket_name, s3_import_cmd)
        # s3 upload puts DL progress to stderr
        s3_upload = subprocess.Popen(shlex.split(s3_import_cmd), stderr=subprocess.PIPE)
        while True:
            progress = s3_upload.stderr.readline()
            if progress == '' and s3_upload.poll() is not None:
                break
            if progress:
                print (progress)
        rc = s3_upload.poll()
        if rc != 0:
            raise subprocess.CalledProcessError(rc)
        print "Upload completed successfully"

    def wait_for_import_to_complete(self, import_id, region='us-east-1'):
        """
        Monitors the status of aws import, waiting for it to complete, or error out
        :param import_id: id of import task to monitor
        """
        task_running = True
        while task_running:
            import_status_cmd = "aws ec2 --profile {}  --region '{}' --output 'json' describe-import-image-tasks --import-task-ids {}".format(self.aws_project, region, import_id)
            res = subprocess.check_output(shlex.split(import_status_cmd))
            print "Current status: {}".format(res)
            res_json = json.loads(res)
            task_running, image_id = self.check_task_status_and_id(res_json)

    @staticmethod
    def check_task_status_and_id(task_json):
        """
        Read status of import json and parse
        :param task_json: status json to parse
        :return: (stillRunning, imageId)
        """
        if task_json.get('ImportImageTasks') is not None:
            task = task_json['ImportImageTasks'][0]
        else:
            task = task_json

        current_status = task['Status']
        image_id = task['ImportTaskId']
        if current_status == 'completed':
            print "The import has completed succesfully as ID: {}".format(image_id)
            return False, image_id
        elif current_status == 'deleting':
            print "The import job has been cancelled for some reason"
            return False, None
        elif current_status == 'deleted':
            print "The import job was cancelled"
            return False, None
        else:
            print "The current import job for id {} status is: {}".format(image_id, current_status)
            print "sleeping for 30 seconds"
            time.sleep(30)
            return True, image_id

    def import_vmdk(self):
        """
        All actions necessary to import vmdk (calls s3 upload, and import to aws ec2)
        :param vmdk_location: location of vmdk to import. Can be provided as a string, or the result output of fabric
        execution
        :return:
        """
        # Set the inital upload to be the first region in the list
        first_upload_region = self.aws_regions[0]

        print "Initial AMI will be created in: {}".format(first_upload_region)
        self.upload_to_s3(region=first_upload_region)
        # If the upload was successful, the name to reference for import is now the basename
        description = "AMI upload of: {}".format(os.path.basename(self.upload_file))
        temp_fd, file_location = self.create_config_file(os.path.basename(self.upload_file), description)
        import_id = self.run_ec2_import(file_location, description, first_upload_region)
        self.wait_for_import_to_complete(import_id)
        self.rename_image(import_id, self.ami_name, source_region=first_upload_region)
        return import_id
    




