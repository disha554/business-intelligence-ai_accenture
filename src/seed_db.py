import sqlite3
from pathlib import Path
DB=Path(__file__).resolve().parents[1]/"data"/"business.db"
c=sqlite3.connect(DB)
c.executescript("""
DROP TABLE IF EXISTS sales; DROP TABLE IF EXISTS product_analytics;
DROP TABLE IF EXISTS incidents; DROP TABLE IF EXISTS deployments; DROP TABLE IF EXISTS operations;
CREATE TABLE sales(date TEXT,region TEXT,product TEXT,segment TEXT,revenue REAL,expected_revenue REAL,units INTEGER);
CREATE TABLE product_analytics(timestamp TEXT,region TEXT,product TEXT,channel TEXT,traffic REAL,checkout_conversion REAL);
CREATE TABLE incidents(timestamp TEXT,service TEXT,event_type TEXT,ticket_count INTEGER);
CREATE TABLE deployments(timestamp TEXT,service TEXT,version TEXT);
CREATE TABLE operations(date TEXT,region TEXT,product TEXT,inventory REAL,delivery_delay REAL);
""")
c.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?,?)",[
("2026-04-05","West","Product X","Enterprise",91800,103000,920),
("2026-04-05","East","Product X","Enterprise",111000,110000,1100),
("2026-04-05","North","Product Y","SMB",78000,79000,1200)])
c.executemany("INSERT INTO product_analytics VALUES (?,?,?,?,?,?)",[
("2026-04-05 09:00","West","Product X","web",10000,.082),
("2026-04-05 10:00","West","Product X","web",10020,.081),
("2026-04-05 11:00","West","Product X","web",10010,.071),
("2026-04-05 12:00","West","Product X","web",10030,.072)])
c.executemany("INSERT INTO incidents VALUES (?,?,?,?)",[
("2026-04-05 09:30","payment-service","payment_failure",42),
("2026-04-05 10:12","payment-service","deployment",1),
("2026-04-05 10:30","payment-service","payment_failure",57),
("2026-04-05 11:00","payment-service","payment_failure",182),
("2026-04-05 12:00","payment-service","payment_failure",180)])
c.execute("INSERT INTO deployments VALUES (?,?,?)",("2026-04-05 10:12","payment-service","v4.8.1"))
c.executemany("INSERT INTO operations VALUES (?,?,?,?,?)",[
("2026-04-05","West","Product X",700,2.0),("2026-04-04","West","Product X",1000,1.0),("2026-04-05","East","Product X",1100,.8)])
c.commit(); c.close()

