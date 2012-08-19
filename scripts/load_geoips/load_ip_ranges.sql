TRUNCATE table geoip_iprange;
ALTER DATABASE `openmonitor` DEFAULT CHARACTER SET latin2 COLLATE latin2_general_ci;
LOAD DATA LOCAL INFILE 'GeoLiteCity_20120807/GeoLiteCity-Blocks.csv' INTO TABLE geoip_iprange CHARACTER SET latin1 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' (start_number,end_number,location_id);
