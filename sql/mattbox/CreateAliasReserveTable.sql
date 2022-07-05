DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateAliasReserveTable`
BEGIN
	drop table if exists alias_reserve;

	create table alias_reserve (alias_id int unique not null, tstamp datetime, reserver varchar(128), primary key (`alias_id`), constraint `no_dups` foreign key (alias_id) references alias(id));

END
/MANGINA/
DELIMITER ;
