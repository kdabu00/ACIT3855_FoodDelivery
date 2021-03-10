import mysql.connector

db_conn = mysql.connector.connect(host="mysql-food-delivery-app-lab6.eastus2.cloudapp.azure.com", user="root",
                                  password="P@ssw0rd", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
    DROP TABLE pickup, delivery
    ''')

db_conn.commit()
db_conn.close()