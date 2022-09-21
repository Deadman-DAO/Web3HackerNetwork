DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateLogTable`()
BEGIN
	drop table if exists log;

	create table log (id int not null auto_increment, tstamp datetime(3), message varchar(2048), primary key (`id`));
END
/MANGINA/
DELIMITER ;
