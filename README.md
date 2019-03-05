# Flights informer

Command line application for searching available flights from flybulgarien.dk

## Flights informer command line arguments

```
usage: main.py [-h] [-return_date RETURN_DATE] dep_city dest_city dep_date persons

Flight informer

positional arguments:
  dep_city              departure city IATA code
  dest_city             destination city IATA code
  dep_date              outbound flight date
  persons               total number of persons

optional arguments:
  -h, --help            show this help message and exit
  -return_date          inbound flight date
```

## Examples

### One-way flight from Burgas (BOJ) to Billund (BLL) for 2 persons

```Bash
python main.py BOJ BLL 01.07.2019 2
```

#### Output

```Bash
Direction    Date              Departure  Arrival    Flight duration From                 To                   Price         Additional information
Outbound     Mon, 1 Jul 19     16:00      17:50      01:50           Burgas (BOJ)         Billund (BLL)        210.00 EUR
```

### Two-way trip from Copenhagen (CPH) to Burgas (BOJ) for 4 persons

```Bash
python main.py CPH BOJ 26.06.2019 4 -return_date=04.07.2019
```

#### Output

```Bash
Direction    Date              Departure  Arrival    Flight duration From                 To                   Price         Additional information
Outbound     Wed, 26 Jun 19    02:45      06:25      03:40           Copenhagen (CPH)     Burgas (BOJ)         580.00 EUR
Inbound      Thu, 4 Jul 19     00:05      01:55      01:50           Burgas (BOJ)         Copenhagen (CPH)     580.00 EUR
Total cost   1160.00 EUR
```
