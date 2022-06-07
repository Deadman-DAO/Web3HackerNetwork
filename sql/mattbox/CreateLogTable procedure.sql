CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`CreateLogTable`()
BEGIN
	drop table if exists log;

	create table log (id int not null auto_increment, tstamp datetime, message varchar(2048), primary key (`id`));
END