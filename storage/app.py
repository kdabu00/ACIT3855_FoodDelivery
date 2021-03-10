import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Storage.base import Base
from Storage.pickup import Pickup
from Storage.delivery import Delivery
import yaml
import logging.config
import logging
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(
    'mysql+pymysql://' + app_config['datastore']['user'] + ':' + app_config['datastore']['password'] +
    '@' + app_config['datastore']['hostname'] + ':' + app_config['datastore']['port'] + '/' + app_config['datastore'][
        'db'])

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def report_pickup_order(body):
    session = DB_SESSION()
    logger.debug('Stored event pickup request with a unique id of ' + body['order_id'])
    po = Pickup(body['customer_id'],
                body['order_id'])

    session.add(po)
    session.commit()
    session.close()


def report_delivery_order(body):
    session = DB_SESSION()
    logger.debug('Stored event delivery request with a unique id of ' + body['order_id'])
    do = Delivery(body['customer_id'],
                  body['order_id'],
                  body['driver_id'])

    session.add(do)

    session.commit()
    session.close()


def get_pickup_orders(timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    print(timestamp_datetime)
    orders = session.query(Pickup).filter(Pickup.date_created >=
                                          timestamp_datetime)
    results_list = []
    for order in orders:
        results_list.append(order.to_dict())

    session.close()
    logger.info("Query for Pickup orders after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200


def get_delivery_orders(timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    print(timestamp_datetime)
    orders = session.query(Delivery).filter(Delivery.date_created >=
                                            timestamp_datetime)
    results_list = []
    for order in orders:
        results_list.append(order.to_dict())

    session.close()
    logger.info("Query for Delivery orders after %s returns %d results" %
                (timestamp, len(results_list)))
    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consumer on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).

    consumer = topic.get_simple_consumer(consumer_group=b'event_group', reset_offset_on_start=False, auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "pickup":
            # Store the event1 (i.e., the payload) to the DB
            report_pickup_order(payload)
        elif msg["type"] == "delivery":
            # Store the event2 (i.e., the payload) to the DB
            report_delivery_order(payload)
        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    logger.info(
        'Connecting to DB. Hostname:' + app_config['datastore']['hostname'] + ', Port:' + app_config['datastore'][
            'port'])
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)

