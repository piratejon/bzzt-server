#!/usr/bin/python2

import gzip
import sys

def make_hpf_record(line):
#54570994845172,z-score
  parts = line.split(',')
  return (int(float(parts[0])), float(parts[1]))

def make_gps_record(line):
#54574126601618,35.44271268,-97.59743031
# or;
#54574126601618,35.44271268,-97.59743031,1234567890better_nano_seconds!
  parts = line.split(',')
  if len(parts) == 4:
    return (int(parts[3]), parts[1], parts[2])
  else:
    return (int(parts[0]), parts[1], parts[2])

def make_better_gps_record(i, rec, zscore):
# sequence number, latitude, longitude, z-score
  return (i, rec[1], rec[2], zscore)

def b_string(b):
  return "{},{},{},{}".format(b[0], b[1], b[2], b[3])

def main2(opened_hpfc, opened_gps):
# first arg is hpfc, second is gps
  gps = []
  hpf = []

  opened_gps.readline() # waste first line
  for line in opened_gps:
    try:
      gps.append(make_gps_record(line.strip()))
    except:
      break
  for line in opened_hpfc:
    hpf.append(make_hpf_record(line.strip()))
    
  better_gps = []
  hpf_start = 0

  for i in range(1, len(gps)):
    # compare the time keys
    while hpf[hpf_start][0] < gps[i-1][0]:
      hpf_start += 1

    hpf_best = 0;
    while hpf[hpf_start][0] < gps[i][0]:
      hpf_best = max(hpf[hpf_start][1], hpf_best)
      hpf_start += 1

    better_gps.append(make_better_gps_record(i, gps[i-1], hpf_best))

  for b in better_gps:
    yield(b)

def main(hpfc_filename, gps_filename_gz):
  with open(hpfc_filename, "r") as hpfc_file, gzip.open(gps_filename_gz, "rb") as gps_file:
    main2(hpfc_file, gps_file)

if __name__=='__main__':
  main(sys.argv[1], sys.argv[2])

