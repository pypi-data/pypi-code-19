import itculate_sdk as itsdk

# Crayon's API keys
api_key = "AXiBsa9t5h51J8H5NEHy8HHGkoFZObtZ"
api_secret = "ArR7QvFcuy2vtb9hFbuhzbZc1WoJ4662Pkh3KZoCkyZOXmqSh36U4B6vN0uzesNJ"
tenant_id = "3gdSPkRsevw3fUirbSiNzB"

# This is the identifier used to detect changes.
# All of the collector's report should be 'flushed' together (use Flusher for that)
collector_id = "crayon_demo"

server_url = "http://localhost:5000/api/v1"
# server_url = "https://api.itculate.io/api/v1"


itsdk.init(server_url=server_url, api_key=api_key, api_secret=api_secret)

with itsdk.Flusher():
    # RDS - arn:aws:rds:us-west-2:214051507508:db:crayoninstance
    # S3 crayon-production-data
    # S3 crayon-production-data
    # S4 m80labs-crayon-raw-screenshots
    # Mac-minis DC (x10)
    # SQS -
    # Job01 Picks job from RDS, puts in SQS (web-kit).
    # MacMinis pulling from SQS, produce a screen shots => Write to S3 (raw screenshots) => SQS message (web-complete)
    # Auto scale (Crayon Job auto-scaler) Job workers (spot instances) => Take from SQS (web-complete) => process =>
    #     writes to S3 (Production data) => Thumbnails (into S3 Production thumbnails)
    # When done => write back to RDS
    # New jobs...

    job_01_instance = "i-b9bf307e"
    worker_auto_scaling = "CrayonJobWorkerAuto"
    s3_raw_screenshots = "m80labs-crayon-raw-screenshots"

    sqs_webkit_in = itsdk.add_vertex(collector_id=collector_id,
                                     name="sqs_webkit_in",
                                     vertex_type="SQS",
                                     keys="webkit2png_standard")

    itsdk.connect(collector_id=collector_id,
                  source=job_01_instance,
                  target=sqs_webkit_in,
                  topology="ab")

    sqs_webkit_out = itsdk.add_vertex(collector_id=collector_id,
                                      name="sqs_webkit_out",
                                      vertex_type="SQS",
                                      keys="webkit2png_completed")

    mac_minis = itsdk.add_vertex(collector_id=collector_id,
                                 name="mac_minis",
                                 vertex_type="Mac",
                                 keys="mac_minis")

    itsdk.connect(collector_id=collector_id,
                  source=mac_minis,
                  target=sqs_webkit_in,
                  topology="ab")

    itsdk.connect(collector_id=collector_id,
                  source=mac_minis,
                  target=sqs_webkit_out,
                  topology="ab")

    itsdk.connect(collector_id=collector_id,
                  source=s3_raw_screenshots,
                  target=mac_minis,
                  topology="ab")

    itsdk.connect(collector_id=collector_id,
                  source=worker_auto_scaling,
                  target=sqs_webkit_out,
                  topology="ab")

