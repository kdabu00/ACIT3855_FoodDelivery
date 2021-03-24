import connexion
import yaml
import logging.config
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from connexion import NoContent
import datetime
import os
import requests
import json
from flask_cors import CORS, cross_origin

headers = {"Content-Type": "application/json"}

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    if not os.path.exists(app_config['datastore']['filename']):
        timestamp = "2021-02-18 08:49:44"
        stats = {'num_delivery_orders': 0, 'num_pickup_orders': 0, 'last_updated': ''}
    else:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)
        timestamp = str(datetime.datetime.strptime(stats['last_updated'], '%Y-%m-%d %H:%M:%S'))

    current = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    r_deliveries = requests.get(app_config['eventstore']['url'] + '/delivery?timestamp=' + timestamp)
    r_pickups = requests.get(app_config['eventstore']['url'] + '/pickup?timestamp=' + timestamp)

    if (r_deliveries.status_code != 200) or (r_pickups.status_code != 200):
        logger.error('Invalid Request')
    else:
        deliveries = r_deliveries.json()
        pickups = r_pickups.json()
        stats['num_pickup_orders'] += len(pickups)
        stats['num_delivery_orders'] += len(deliveries)
        stats['last_updated'] = str(current)

        logger.info(str((len(pickups) + len(deliveries))) + " events received")

        f = open(app_config['datastore']['filename'], 'w')
        json.dump(stats, f, indent=2)
        f.close()
        logger.debug('num_pickup_orders -> %d num_delivery_orders -> %d' % (stats['num_pickup_orders'],
                                                                            stats['num_delivery_orders']))
    logger.info('End of Periodic Processing')


def get_stats():
    logger.info('Requesting Stats')
    if not os.path.exists('data.json'):
        logger.error('Statistics do not exist')
        return NoContent, 404
    else:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)
            stat_dict = {'num_delivery_orders': stats['num_delivery_orders'],
                         'num_pickup_orders': stats['num_pickup_orders']}
    logger.debug(stat_dict)
    logger.info('Request Completed')
    return stat_dict, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
