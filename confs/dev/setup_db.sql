CREATE DATABASE `todo` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
  
#create user
CREATE USER 'cacti'@'localhost' IDENTIFIED BY 'cacti';
GRANT ALL ON *.* TO 'cacti'@'localhost';
  
CREATE USER 'cacti'@'%' IDENTIFIED BY 'cacti';
GRANT ALL ON *.* TO 'cacti'@'%';

