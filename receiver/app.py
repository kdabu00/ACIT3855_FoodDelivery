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


def report_pickup_order(body):
    logger.info('Received event pickup request with a unique id of ' + body['order_id'])
    client = KafkaClient(hosts=app_config['events']['hostname']+':'+app_config['events']['port'])
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = {"type": "pickup", "datetime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info('Returned event pickup response (Id:'+body['order_id']+') with status 201')


def report_delivery_order(body):
    logger.info('Received event delivery request with a unique id of ' + body['order_id'])
    client = KafkaClient(hosts=app_config['events']['hostname']+':'+app_config['events']['port'])
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = {"type": "delivery", "datetime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info('Returned event pickup response (Id:'+body['order_id']+') with status 201')


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)
