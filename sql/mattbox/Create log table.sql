use w3hacknet
DROP PROCEDURE IF EXISTS w3hacknet.CreateLogTable;

DELIMITER $$
$$
CREATE PROCEDURE w3hacknet.CreateLogTable()
BEGIN
	drop table if exists log;

	create table log (id int not null auto_increment, tstamp datetime, message varchar(2048), primary key (`id`));
end
$$
DELIMITER ;
;
