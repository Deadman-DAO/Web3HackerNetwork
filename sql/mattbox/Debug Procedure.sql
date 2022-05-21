CREATE PROCEDURE w3hacknet.debug(
message varchar(2048))
BEGIN 
 	declare tstamp datetime default now();
	insert into log (tstamp, message) select tstamp, message;
END