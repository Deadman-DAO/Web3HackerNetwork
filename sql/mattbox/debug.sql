DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`debug` (
IN message varchar(2048)
)
BEGIN 
 	declare tstamp datetime default current_timestamp(3);
	insert into log (tstamp, message) select tstamp, message;
END
/MANGINA/
DELIMITER ;
