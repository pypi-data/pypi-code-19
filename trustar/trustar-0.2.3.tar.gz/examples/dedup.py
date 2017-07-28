import pickle
import os
from trustar import TruStar

deleted_guids = {}

if os.path.isfile('deleted_guids.pkl'):
    with open('deleted_guids.pkl', 'rb') as f:
        deleted_guids = pickle.load(f)

with open('guid_dictionary.pkl', 'rb') as f:
    guids = pickle.load(f)

    guids_to_delete = []  # A list of all of the guids that need to be deleted
    parent_guids = guids.keys()  # A list of all the guids that are being kept.
    for parent_guid in parent_guids:
        for value in guids[parent_guid]:
            if value not in deleted_guids:
                guids_to_delete.append(value)

    ts = TruStar(config_role="production")
    token = ts.get_token()

    max_delete = 5000
    num_deleted = 0
    num_attempts = 0

    try:
        print("Found %d reports to delete" % (len(guids_to_delete)))
        for to_delete in guids_to_delete:
            num_attempts += 1
            result = ts.get_report_details(token, to_delete, id_type="internal")

            if result.get('id') != to_delete:
                print("Could not find report %s" % to_delete)
                deleted_guids[to_delete] = None
            else:
                response = ts.delete_report(token, report_id=to_delete, id_type="internal")
                print("Report %s deleted (%d/%d) " % (to_delete, num_deleted, max_delete))
                deleted_guids[to_delete] = None
                num_deleted += 1

            # refresh token
            if num_attempts % 50 == 0:
                token = ts.get_token()
            if num_attempts >= max_delete:
                break

    except Exception as e:
        print(e)

    finally:
        # write the 'new' db to the file.
        with open('deleted_guids.pkl', 'wb') as pf:
            pickle.dump(deleted_guids, pf)

        print("Deleted %d reports!" % num_deleted)
