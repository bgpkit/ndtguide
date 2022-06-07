# NDTGuide

NDTGuide is a Python package that aims to provide easy to use quick access to MeasurementLab's (MLab)
NDT measurement data on Google BigQuery. This library is intended to work **only** on Google Colab
platform due to the BigQuery and GCP's requirement on service account usage.

## Overview

`NDTGuide` provides an abstract layer around the Google BigQuery interface and MLab's data 
schema. At its core, it provides a growing number of functions that translate user intentions
into BigQuery SQL statements.

## Usage

### Login with Google Account (Required Step)

Since the MLab's data access is tied to individual Google accounts, it is required to first
login to Google first when first running the script. `NDTGuide` provided a wrapper `.login()` 
function that interactively prompt user to login.

```python
guide = NDTGuide()
guide.login()
```

### Gather Daily NDT Stats

One of the most used queries is to pull out daily aggregated statistics of the measurement data
to gather some overview of certain clients/servers/regions. `NDTGuide` provides the `.sql_daily_aggregate(...)`
function to generate sql statements for this task.

It accepts the following required parameters:
- `table_name`: currently supports `ndt7` or `ndt5`
- `date_start` and `date_end`: start and end date, in the format of `YYYY-mm-dd`
- `aggr_func`: aggregation function, currently supports `avg`, `max`, `min`

Additional filters for NDT clients and servers include:
- `client_asn` and `server_asn`: autonomous number of the client/server
- `client_cidr` and `server_cidr`: IP block (CIDR) of  the client/server
- `client_country` and `server_country`: two-letter country code of the client/server

The query should return results of the following data:
- mean throughput
- minimum RTT
- packet loss rate

The following example queries the average measurements from `ndt7` table between `2022-02-01` to 
`2022-02-10` for clients located in Ukraine.
```python
sql = guide.sql_daily_aggregate("ndt7", "2022-02-01", "2022-02-10", "avg", client_country="ua")
guide.exec_sql(sql)
```

```text
|   | avg_throughput |   avg_rtt | avg_lossrate |       date |
| 0 |      49.453097 | 52.033121 |     0.042338 | 2022-02-01 |
| 1 |      50.410214 | 53.451678 |     0.051775 | 2022-02-02 |
| 2 |      52.047963 | 52.372124 |     0.043772 | 2022-02-03 |
| 3 |      54.767157 | 55.180171 |     0.041808 | 2022-02-04 |
| 4 |      47.897135 | 58.383362 |     0.029880 | 2022-02-05 |
| 5 |      75.044735 | 59.411379 |     0.041825 | 2022-02-06 |
| 6 |      91.473595 | 49.754529 |     0.048684 | 2022-02-07 |
| 7 |      58.433473 | 48.761221 |     0.041670 | 2022-02-08 |
| 8 |     105.985296 | 56.598006 |     0.034676 | 2022-02-09 |
| 9 |      64.017782 | 57.256041 |     0.045156 | 2022-02-10 |
```

### Gather Clients and Servers

`NDTGuide` provides function to generate queries look for
- clients that users servers in certain network
- servers that the clients in certain network uses

These functions allow users to quickly locate relevant clients/servers for any interested networks.

For example, the following query gathers all the NDT servers any clients from AS3216 used during a one week period:
```python
sql = guide.sql_get_servers("ndt7", "2022-01-01", "2022-01-07", "3216")
print(sql)
df = guide.exec_sql(sql)
df
```

```text
      SELECT distinct server.Site, server.Machine, server.Network.ASNumber, server.Network.ASName, server.Network.CIDR, server.Geo.CountryCode, server.Geo.City
      FROM `measurement-lab.ndt.ndt7` 
      WHERE date>='2022-01-01' and date<='2022-01-07'  and client.Network.ASNumber=3216
      
|    | Site  | Machine | ASNumber | ASName                            | CIDR               | CountryCode | City      |
|----+-------+---------+----------+-----------------------------------+--------------------+-------------+-----------|
|  0 | beg01 | mlab1   |    13004 | Serbian Open Exchange DOO         | 188.120.127.0/26   | RS          | Belgrade  |
|  1 | arn03 | mlab1   |     3356 | Level 3 Parent, LLC               | 213.242.86.64/26   | SE          | Stockholm |
|  2 | beg01 | mlab2   |    13004 | Serbian Open Exchange DOO         | 188.120.127.0/26   | RS          | Belgrade  |
|  3 | arn04 | mlab2   |     1299 | Telia Company AB                  | 62.115.225.128/26  | SE          | Stockholm |
|  4 | arn05 | mlab3   |     3257 | GTT Communications Inc.           | 77.67.119.64/26    | SE          | Stockholm |
|  5 | arn03 | mlab2   |     3356 | Level 3 Parent, LLC               | 213.242.86.64/26   | SE          | Stockholm |
|  6 | beg01 | mlab3   |    13004 | Serbian Open Exchange DOO         | 188.120.127.0/26   | RS          | Belgrade  |
|  7 | arn02 | mlab3   |     1273 | Vodafone Group PLC                | 195.89.146.192/26  | SE          | Stockholm |
|  8 | hnd02 | mlab1   |     2518 | BIGLOBE Inc.                      | 210.151.179.128/26 | JP          | Tokyo     |
|  9 | arn06 | mlab3   |     6453 | TATA COMMUNICATIONS (AMERICA) INC | 193.142.125.64/26  | SE          | Stockholm |
| 10 | arn04 | mlab1   |     1299 | Telia Company AB                  | 62.115.225.128/26  | SE          | Stockholm |
| 11 | arn06 | mlab2   |     6453 | TATA COMMUNICATIONS (AMERICA) INC | 193.142.125.64/26  | SE          | Stockholm |
| 12 | arn04 | mlab3   |     1299 | Telia Company AB                  | 62.115.225.128/26  | SE          | Stockholm |
| 13 | hnd04 | mlab1   |     5580 | GTT Netherlands B.V.              | 64.235.255.128/26  | JP          | Tokyo     |
| 14 | arn05 | mlab1   |     3257 | GTT Communications Inc.           | 77.67.119.64/26    | SE          | Stockholm |
| 15 | arn02 | mlab1   |     1273 | Vodafone Group PLC                | 195.89.146.192/26  | SE          | Stockholm |
| 16 | arn02 | mlab2   |     1273 | Vodafone Group PLC                | 195.89.146.192/26  | SE          | Stockholm |
| 17 | hnd03 | mlab1   |     2516 | KDDI Corporation                  | 111.109.1.64/26    | JP          | Tokyo     |
| 18 | hnd04 | mlab3   |     5580 | GTT Netherlands B.V.              | 64.235.255.128/26  | JP          | Tokyo     |
| 19 | arn05 | mlab2   |     3257 | GTT Communications Inc.           | 77.67.119.64/26    | SE          | Stockholm |
| 20 | hnd03 | mlab3   |     2516 | KDDI Corporation                  | 111.109.1.64/26    | JP          | Tokyo     |
| 21 | arn06 | mlab1   |     6453 | TATA COMMUNICATIONS (AMERICA) INC | 193.142.125.64/26  | SE          | Stockholm |
| 22 | arn03 | mlab3   |     3356 | Level 3 Parent, LLC               | 213.242.86.64/26   | SE          | Stockholm |
```

### Customizable Queries

`NDTGuide` provide a `.get_schema()` function to provide a selected useful schema to help with
manually constructing BigQuery queries.

```python
guide.get_schema()
```

```python
{'a': {'CongestionControl': 'string',
  'LossRate': 'float',
  'MeanThroughputMbps': 'float',
  'MinRTT': 'float',
  'TestTime': 'TimeStamp',
  'UUID': 'string'},
 'client': {'Geo': {'City': 'string',
   'ContinentCode': 'string',
   'CountryCode': 'string',
   'CountryName': 'string'},
  'Network': {'ASName': 'string', 'ASNumber': 'integer', 'CIDR': 'string'}},
 'date': 'date',
 'id': 'string',
 'server': {'Geo': {'City': 'string',
   'ContinentCode': 'string',
   'CountryCode': 'string',
   'CountryName': 'string'},
  'Machine': 'string',
  'Network': {'ASName': 'string', 'ASNumber': 'integer', 'CIDR': 'string'},
  'Site': 'string'}}
```

The customized queries can be passed into the same `.exec_sql(sql)` function similar to other 
provided built-in functions.