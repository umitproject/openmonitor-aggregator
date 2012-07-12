#!/bin/sh
echo "Starting download geoip data..."
python download.py
rm -rf GeoLiteCity*.zip
echo "Importing location data into mysql..."
mysql -uroot -proot --local-infile=1 openmonitor<load_geoips.sql
echo "Filling location names..."
python fill_geoips.py --country-names --fullnames
echo "Importing iprange data into mysql..."
mysql -uroot -proot --local-infile=1 openmonitor<load_ip_ranges.sql
