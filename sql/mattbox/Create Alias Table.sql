drop table alias 
create table alias (id int not null AUTO_INCREMENT primary key, md5 char(32) not null, name varchar(256), count int default 0)
create unique index aliasIdx on alias (md5)
