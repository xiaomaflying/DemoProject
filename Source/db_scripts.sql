create database if not exists crossover;
use crossover;
create table sysinfo (id integer(10) primary key auto_increment, ip varchar(20) not null, user varchar(64) not null, email varchar(100) not null, info longtext);
