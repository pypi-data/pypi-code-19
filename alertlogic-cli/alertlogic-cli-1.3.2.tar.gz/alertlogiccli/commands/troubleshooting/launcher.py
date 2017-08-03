import alertlogiccli.command
import json

class Redeploy(alertlogiccli.command.Command):
    """Redeploys customer's entire deployment or VPC"""
    
    def configure_parser(self, subparsers):
        parser = subparsers.add_parser("redeploy", help="Redeploys customer's entire deployment or VPC")
        parser.set_defaults(command=self)
        
        parser.add_argument("--vpc_key", nargs="?")
        parser.add_argument("--hard", nargs="?")
    
    def execute(self, context):
        args = context.get_final_args()
        launcher_remediation = context.get_services().launcher_remediation
        
        response = launcher_remediation.redeploy(account_id=args["account_id"],
                                                 environment_id=args["deployment_id"],
                                                 vpc_key=args["vpc_key"],
                                                 hard=args["hard"])
        print(response.content)
        return response