DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`test` (
IN rslt_alias_id int(11)
)
BEGIN
	declare halfway_point datetime;
		select FROM_UNIXTIME( 
			((UNIX_TIMESTAMP(max(date))-UNIX_TIMESTAMP(min(date)))/2)+UNIX_TIMESTAMP(min(date)) 
			)
		  into @dunno
		from commit where alias_id = rslt_alias_id;
END
/MANGINA/
DELIMITER ;
