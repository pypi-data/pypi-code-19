"""
Script to be run on a new MongoDB that need to join a remote MongoDB RS.
This script will connect to the remote RS, and make the RS add this new host to itself.
"""

import sys
import ssl
import socket
import pprint
import pymongo
import logbook
import argparse

logbook.StreamHandler(sys.stdout).push_application()
logger = logbook.Logger("JoinRs")

def join_rs(rs_client: pymongo.MongoClient, my_hostname: str, hidden:bool=False, priority:float=1.0, leave:bool=False):
    """
    Connect to the RS using rs_client, and then add my_hostname (That is by default the host running this script) to the RS)
    """

    logger.info("Connecting to existing RS")
    logger.info("Connected !")

    logger.info("Determinating ID for the new host")
    pipeline = [
        {"$unwind": "$members"},
        {"$group": {
            "_id": None,
            "max": {
                "$max": "$members._id"
                }
            }
        }
    ]
    config = list(rs_client.local.system.replset.find({}))[0]
    logger.info("Current RS configuration:\r\n{rs}".format(
        rs=pprint.pformat(config)
    ))
    if not leave:
        last_id_result = list(rs_client.local.system.replset.aggregate(pipeline))
        last_id = last_id_result[0]["max"]
        next_id = last_id + 1
        logger.info("Last ID is [{last_id}], Next ID will be [{next_id}]".format(
            last_id=last_id,
            next_id=next_id
        ))

        new_member = {
            "_id": next_id,
            "host": "{hostname}:27017".format(hostname=my_hostname),
            "priority": priority,
            "hidden": hidden
        }
        
        config["members"].append(new_member)

        logger.info("Joining RS")
    else:
        config["members"].remove(
            [
                key 
                for key in config["members"] 
                if key["host"] == "{hostname}:27017".format(hostname=my_hostname)
            ][0]
        )
        logger.info("Leaving RS")
    
    config["version"] = config["version"] + 1
    rs_client.admin.command("replSetReconfig", config)
    logger.info("Done!")


def main():
    """
    Main entrypoint
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hostname",
        help="The hostname to add to the RS, default to your own hostname",
        default=socket.gethostname()
    )

    parser.add_argument(
        "--connection-string",
        help="The connection string to connect to the RS",
        required=True
    )

    parser.add_argument(
        "--ssl",
        help="Use SSL to connect to the RS",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--priority",
        help="The priority of the host to add",
        type=float,
        default=1.0
    )

    parser.add_argument(
        "--hidden",
        help="Is the new host hidden",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--leave",
        help="Leave the RS instead of joining it",
        action="store_true",
        default=False
    )

    args = parser.parse_args()

    client = pymongo.MongoClient(
        args.connection_string,
        ssl=args.ssl,
        ssl_cert_reqs=ssl.CERT_NONE,
        connect=True
    )

    join_rs(
        client,
        args.hostname,
        args.hidden,
        args.priority,
        args.leave
    )

main()