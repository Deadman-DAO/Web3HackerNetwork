DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`UpdateHackerExtensionCount` (
IN _alias_pk int(11),
IN _extension varchar(64),
IN _count int(11)
)
BEGIN
	declare _ext_pk int;
	call GetFileExtensionPK(_extension, _ext_pk);
	insert into hacker_extension_association (alias_id, extension_id, count) values (_alias_pk, _ext_pk, _count)
		on duplicate key update count = count + _count;
END
/MANGINA/
DELIMITER ;
