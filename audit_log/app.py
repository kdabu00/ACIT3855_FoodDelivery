import connexion
import requests
import yaml
import logging.config
import logging
from connexion import NoContent
import datetime
import json
from pykafka import KafkaClient

headers = {"Content-Type": "application/json"}

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_pickup_order(index):
    """ Get PO Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving PO at index %d" % index)
    try:
        messages = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'pickup':
                messages.append(msg)
        logger.info('Total pickup orders: %d' % len(messages))
        if index < len(messages):
            return messages[index]['payload'], 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find PO at index %d" % index)
    return {"message": "Not Found"}, 404


def get_delivery_order(index):
    """ Get DO Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    print(consumer)
    logger.info("Retrieving DO at index %d" % index)
    try:
        messages = []
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            if msg['type'] == 'delivery':
                messages.append(msg)
        logger.info('Total delivery orders: %d' % len(messages))
        if index < len(messages):
            return messages[index], 200
    except:
        logger.error("No more messages found")

    logger.error("Could not find DO at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
