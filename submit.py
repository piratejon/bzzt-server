#!/usr/bin/python2

import combinefiles
import bzztabase
import urllib2
import gzip
import uuid
import cgi
import os

def count_lines_in_file(f):
  linecount = 0
  while 1:
    line = f.readline()
    if not line: break
    linecount = linecount + 1
  return str(linecount)

def save_file(f1, p):
  with open(p, "wb") as f2:
    while True:
      one_block = f1.read(4096)
      if one_block:
        f2.write(one_block)
      else:
        break

def accel_through_r(infile, outfile):
  os.system('Rscript accel.R {} {}'.format(infile, outfile))

def accel_to_db(accel_a, accel_b):
  accel_through_r(accel_a, accel_b)

def query_rectangle(db, x0, y0, x1, y1):
  return db.query_rectangle(x0, y0, x1, y1)

def query_notices(db, x0, y0, x1, y1):
  return db.query_notices(x0, y0, x1, y1)

def submit_notice(db, remote_addr, user_agent, message_text, latitude, longitude):
  u = str(uuid.uuid4())
  db.insert_source_row(remote_addr, user_agent, u)
  db.insert_notice(urllib2.unquote(message_text), latitude, longitude)
  db.commit()

def submit_points(db, remote_addr, user_agent, accel_file, gps_file):
  u = str(uuid.uuid4())
  db.insert_source_row(remote_addr, user_agent, u)

  accel_a = '/tmp/bzzt-' + u + '.accel-a.txt.gz'
  accel_b = '/tmp/bzzt-' + u + '.accel-b.txt.gz'
  save_file(accel_file, accel_a)

  accel_to_db(accel_a, accel_b)
  # pass gps file object directly to thing that processes it saving a trip to disk
  with open(accel_b, "r") as accel_b_open:
    for record in combinefiles.main2(accel_b_open, gzip.GzipFile(fileobj=gps_file, mode='rb')):
      db.insert_accel_row(record)

  db.commit()

def application(env, start_response):
  start_response('200 OK', [('Content-Type', 'text/plain')])
  post_env = env.copy()
  post = cgi.FieldStorage(fp=env['wsgi.input'], environ=post_env, keep_blank_values=True)

  db = bzztabase.Bzztabase()

  if 'gps' in post and 'accel' in post and post['gps'].file and post['accel'].file:
      submit_points(db, env['REMOTE_ADDR'], env['HTTP_USER_AGENT'], post['accel'].file, post['gps'].file)

  elif 'message' in post:
    submit_notice(db, env['REMOTE_ADDR'], env['HTTP_USER_AGENT'], post['message'].value, post['latitude'].value, post['longitude'].value)

  else:
    qs = cgi.parse_qs(env['QUERY_STRING'])

    want = qs.get('want', [''])[0]
    x0 = qs.get('x0', [''])[0]
    y0 = qs.get('y0', [''])[0]
    x1 = qs.get('x1', [''])[0]
    y1 = qs.get('y1', [''])[0]

    if len(x0) > 0 and len(y0) > 0 and len(x1) > 0 and len(y1) > 0:
      if want == "points":
        for result in query_rectangle(db, float(x0), float(y0), float(x1), float(y1)):
          for row in result:
            yield "{},{},{},{},{}\n".format(row[0], row[1], row[2], row[3], row[4])
      elif want == "notices":
        for result in query_notices(db, float(x0), float(y0), float(x1), float(y1)):
          for row in result:
            yield "{},{},{}\n".format(row[1], row[2], ' '.join(row[0].split('+')))

#return [a for a in post if not a.startswith('__')]

