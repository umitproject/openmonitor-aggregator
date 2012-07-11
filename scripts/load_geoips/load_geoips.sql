TRUNCATE table geoip_iprange;
ALTER DATABASE `openmonitor` DEFAULT CHARACTER SET latin2 COLLATE latin2_general_ci;
LOAD DATA LOCAL INFILE 'GeoLiteCity_20110906/GeoLiteCity-Location.csv' INTO TABLE geoip_location CHARACTER SET latin1 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' (id,country_code,state_region,city,zipcode,lat,lon);
