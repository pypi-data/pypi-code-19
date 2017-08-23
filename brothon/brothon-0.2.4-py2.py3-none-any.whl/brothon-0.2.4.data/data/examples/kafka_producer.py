from kafka import KafkaProducer
from time import sleep
from datetime import datetime

producer = KafkaProducer(bootstrap_servers='localhost:9092')

while 1:
  # "kafkaesque" is the name of our topic
  producer.send("shit-butt", str.encode("Metamorphosis! " + str(datetime.now().time()) ))
  sleep(1)
