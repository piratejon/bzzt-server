#!/usr/bin/python2

import psycopg2

class Bzztabase:
  def __init__(self):
    self.conn = psycopg2.connect("dbname='bzzt' user='bzzt' host='localhost' password=''")

  def query_rectangle(self, x0, y0, x1, y1):
    self.cursor = self.conn.cursor()
    query_string = "select fk_source, sequence_id, ST_X(loc), ST_Y(loc), zscore from accel where accel.loc && ST_MakeEnvelope(%s,%s,%s,%s, 4326) order by fk_source, sequence_id"
#    query_string = "select array_to_json(array_agg(row_to_json(t))) from (select sequence_id, ST_X(loc), ST_Y(loc), zscore from accel where accel.loc && ST_MakeEnvelope(%s, %s, %s, %s, 4326) order by fk_source, sequence_id) t"
    self.cursor.execute(query_string, (x0, y0, x1, y1))
    yield self.cursor.fetchall()

  def query_notices(self, x0, y0, x1, y1):
    self.cursor = self.conn.cursor()
    query_string = "select message, ST_X(loc), ST_Y(loc) from notice where notice.loc && ST_MakeEnvelope(%s,%s,%s,%s, 4326)"
    self.cursor.execute(query_string, (x0, y0, x1, y1))
    yield self.cursor.fetchall()

  def insert_source_row(self, remote_addr, user_agent, uuid):
    self.cursor = self.conn.cursor()
    insert_string = "INSERT INTO source (sequence, network_address, uas) VALUES (%s,%s,%s) RETURNING id"
    self.cursor.execute(insert_string, (uuid, remote_addr, user_agent))
    self.rowid = self.cursor.fetchone()[0]

  def insert_accel_row(self, record):
# record is tuple of sequence id, lat, long, z-score
    pt = "POINT(%s %s)" % (float(record[1]), float(record[2]))
    insert_string = "INSERT INTO accel(fk_source, sequence_id, loc, zscore) VALUES (%s,%s,ST_GeomFromText(%s,4326),%s)"
    self.cursor.execute(insert_string, (self.rowid, int(record[0]), pt, float(record[3])))

  def insert_notice(self, message_text, latitude, longitude):
    pt = "POINT(%s %s)" % (float(latitude), float(longitude))
    insert_string = "INSERT INTO notice(fk_source, message, loc) VALUES (%s,%s,ST_GeomFromText(%s,4326))"
    self.cursor.execute(insert_string, (self.rowid, message_text, pt))

  def commit(self):
    self.conn.commit()

