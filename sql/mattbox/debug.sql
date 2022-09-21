DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`debug` (
IN message longblob
)
BEGIN 
 	declare tstamp datetime(3) default current_timestamp(3);
	insert into log (tstamp, message) select tstamp, left(message, 2047);
END
/MANGINA/
DELIMITER ;
