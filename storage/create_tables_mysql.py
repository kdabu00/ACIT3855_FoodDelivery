import mysql.connector
db_conn = mysql.connector.connect(host="mysql-food-delivery-app-lab6.eastus2.cloudapp.azure.com", user="root", password=, database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
          CREATE TABLE pickup
          (id INT NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           order_id VARCHAR(250) NOT NULL,
           purchase_date VARCHAR(100) NOT NULL,
           preparation_time VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT pickup_pk PRIMARY KEY (id))
          ''')
db_cursor.execute('''
          CREATE TABLE delivery
          (id INT NOT NULL AUTO_INCREMENT, 
           customer_id VARCHAR(250) NOT NULL,
           order_id VARCHAR(250) NOT NULL,
           driver_id VARCHAR(250) NOT NULL,
           purchase_date VARCHAR(100) NOT NULL,
           preparation_time VARCHAR(100) NOT NULL,
           delivery_time VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT delivery_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
