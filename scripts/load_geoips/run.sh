#!/bin/sh
echo "Starting download geoip data..."
python download.py
rm -rf GeoLiteCity*.zip
echo "Importing location data into mysql..."
mysql -uroot -proot openmonitor<load_geoips.sql
echo "Filling location names..."
python fill_geoips.py --country-names --fullnames
echo "Importing iprange data into mysql..."
mysql -uroot -proot openmonitor<load_ip_ranges.sql
echo "Filling ip range data..."
python fill_ip_ranges.py
