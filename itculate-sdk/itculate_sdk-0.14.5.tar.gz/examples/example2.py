import random
import itculate_sdk as itsdk
from unix_dates import UnixDate, UnixTimeDelta

upload_workflow = {
    "Name": "CDR_UPLOAD",
    "vertices": [
        {
            "Name": "Client",
            "Key": "1.1.1.1",
            "Type": "Client",
            "Description": "upload to s3"
        },
        {
            "Name": "CDR Bucket",
            "Key": "cvidyabucket",
            "Type": "S3",
            "Description": "Holds the uploaded cdr"
        },
        {
            "Name": "Zone Dispatcher",
            "Key": "zone-dispatcher",
            "Type": "Worker",
            "Description": "Dispatch CDR by Zone"
        },
        {
            "Name": "ZONE CDR Persister Zone 1",
            "Key": "cdr-persister-1",
            "Type": "Worker",
            "Description": "Write CDR to Database"
        },
        {
            "Name": "ZONE CDR Persister Zone 2",
            "Key": "cdr-persister-2",
            "Type": "Worker",
            "Description": "Write CDR to Database"
        },
        {
            "Name": "ZONE CDR Persister Zone 3",
            "Key": "cdr-persister-3",
            "Type": "Worker",
            "Description": "Write CDR to Database"
        },
        {
            "Name": "Oracle FMSDB",
            "Key": "fmsdb",
            "Type": "Oracle_DB",
            "Description": "Database"
        }
    ],
    "edges": [  # from and to are key of the Vertex
                {"from": "1.1.1.1", "to": "cvidyabucket"},
                {"from": "cvidyabucket", "to": "zone-dispatcher"},
                {"from": "zone-dispatcher", "to": "cdr-persister-1"},
                {"from": "zone-dispatcher", "to": "cdr-persister-2"},
                {"from": "zone-dispatcher", "to": "cdr-persister-3"},
                {"from": "cdr-persister-1", "to": "fmsdb"},
                {"from": "cdr-persister-2", "to": "fmsdb"},
                {"from": "cdr-persister-3", "to": "fmsdb"}
                ]
}

analyze_workflow = {
    "Name": "CDR_ANALYZE",
    "vertices": [
        {
            "Name": "5_min_fraud_analysis_job",
            "Key": "5_min_fraud_analysis_job",
            "Type": "Cron",
            "Description": "Trigger analysis"
        },
        {
            "Name": "Fraud Analysis",
            "Key": "Fraud-Analysis",
            "Type": "Worker",
            "Description": "Analyze to detect frauds"
        },
        {
            "Name": "Analysis Cube",
            "Key": "Analysis-Cube",
            "Type": "Worker",
            "Description": "Build analyze cube"
        },
        {
            "Name": "Extract",
            "Key": "Extract",
            "Type": "Worker",
            "Description": "Extract CDR records from Database"
        },
        {
            "Name": "Oracle FMSDB",
            "Key": "fmsdb",
            "Type": "Oracle_DB",
            "Description": "Database"
        }
    ],
    "edges": [  # from and to are key of the Vertex
                {"from": "5_min_fraud_analysis_job", "to": "Fraud-Analysis"},
                {"from": "Fraud-Analysis", "to": "Analysis-Cube"},
                {"from": "Analysis-Cube", "to": "Extract"},
                {"from": "Extract", "to": "fmsdb"},
                ]
}

collector_id = "collector_id_cvidya"


def build_cvidya_topolgy():
    workflows = [upload_workflow, analyze_workflow]
    # shared infrastructure
    for workflows in workflows:
        for vertex in workflows["vertices"]:
            itsdk.add_vertex(collector_id=collector_id,
                             vertex_type=vertex["Type"],
                             name=vertex["Name"],
                             keys=vertex["Key"],
                             description=vertex["Description"])

        for edge in workflows["edges"]:
            itsdk.connect(collector_id=collector_id,
                          source=edge["from"],
                          target=edge["to"],
                          topology=workflows["Name"])

    itsdk.flush_all()


def send_samples():
    now = UnixDate.now() - UnixTimeDelta.calc(hours=24)
    for workflows in [upload_workflow, analyze_workflow]:
        for vertex in workflows["vertices"]:
            for i in range(24 * 60):
                timestamp = now + UnixTimeDelta.calc(minutes=i)
                itsdk.add_sample(vertex=vertex["Key"],
                                 timestamp=timestamp,
                                 counter="payload-size",
                                 value=itsdk.CapacityDataType.value(5000 * random.random()))
                itsdk.add_sample(vertex=vertex["Key"],
                                 timestamp=timestamp,
                                 counter="total-duration",
                                 value=itsdk.LatencyDataType.value(1000 * random.random()))

        itsdk.flush_all()


if __name__ == '__main__':
    itsdk.init(server_url="http://localhost:5000/api/v1")

    build_cvidya_topolgy()
    send_samples()
