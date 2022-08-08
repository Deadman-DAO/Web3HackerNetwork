DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`GetFileExtensionPK` (
IN extension varchar(64),
OUT pk int(11)
)
BEGIN
	set pk = -1;
	select id into pk from file_extension where ext = extension;
	if pk < 1 then
		insert into file_extension (ext) values (extension);
		select LAST_INSERT_ID() into pk;  
	end if;
END
/MANGINA/
DELIMITER ;
