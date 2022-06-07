CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`debug`(
message varchar(2048))
BEGIN 
 	declare tstamp datetime default current_timestamp(4);
	insert into log (tstamp, message) select tstamp, message;
END