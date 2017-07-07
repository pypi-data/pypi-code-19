
from django_framework.django_helpers.worker_helpers import BaseWorker

from django_framework.django_helpers.worker_helpers.worker_registry import register_worker


class BasicTestRunWorker(BaseWorker):
    ALLOWED_JOBS = {
        "update" : {
                        'self' : {'job_type' : ['synchronous', 'local', 'asynchronous'], 'timeout' : 3600},
                        'test' : {'job_type' : ['asynchronous'], 'timeout' : 3600},
                        'delete' : {'job_type' : ['local'], 'timeout' : 300},
                    } 
        }
    
    def generate_initial_payload(self, command, action, **kwargs):
        
        if command == 'update':
            if action == 'self':
                return {"command" : "blah", "action" : "blah", "job_timeout" : 1, "scheduled_at" :None}
            elif action == 'test':
                return {"command" : "sdf", "action" : "blah", "job_timeout" : 1, "scheduled_at" :None}
            
        raise ValueError('This job/command is not allowed!')
    
    def process_response(self, worker_response):
        # note that worker_response is always going to a BaseWorkerResponse object
        
        # do everything you need to do in here!!
        if worker_response.command == 'update':
            worker_response = self.process_response_update(worker_response=worker_response)

        else:
            raise ValueError('The command/action for BasicTestRun was not recognized!')
        
        
        return worker_response
    
    def process_response_update(self, worker_response):
        response = {"status" : 0, "error_notes" : None}
        if worker_response.action == 'self':
            response['response'] = 'Ran checks on self.  Everything seems ok!'
        
        
        return response
        
register_worker(BasicTestRunWorker)