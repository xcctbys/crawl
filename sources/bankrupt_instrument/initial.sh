#!/bin/bash

mysql -uroot -p

create database bankrupt;
use bankrupt;

CREATE TABLE IF NOT EXISTS config_table (
	config VARCHAR(100) CHARACTER SET utf8 COLLATE utf8_bin,
	value TEXT CHARACTER SET utf8 COLLATE utf8_bin,
	PRIMARY KEY (config)
);

INSERT INTO config_table (config, value) VALUES ("json_path" 
, "/media/clawer_result/enterprise/json/");
INSERT INTO config_table (config, value) VALUES ("json_host" 
, "10.100.90.51");
INSERT INTO config_table (config, value) VALUES ("pdf_path" 
, "/media/clawer_result/enterprise/pdf/");
INSERT INTO config_table (config, value) VALUES ("pdf_host" 
, "10.100.90.51");

CREATE TABLE IF NOT EXISTS bankrupt_content (
	id INT AUTO_INCREMENT,
	obligor VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_bin,
	event_date VARCHAR(12) CHARACTER SET utf8 COLLATE utf8_bin,
	pdf_path TEXT CHARACTER SET utf8 COLLATE utf8_bin,
	category VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_bin,
	court VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_bin,
	publish_date VARCHAR(12) CHARACTER SET utf8 COLLATE utf8_bin,
	url TEXT CHARACTER SET utf8 COLLATE utf8_bin,
	PRIMARY KEY (id)
);