DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`UpdateHackerImportCount` (
IN _alias_md5 char(32),
IN _import_name varchar(256),
IN _extension varchar(64),
IN _count float
)
BEGIN
	declare _ext_pk int;
	declare _imp_pk int;
	declare _alias_pk int default -1;
	
	select id into _alias_pk from alias where md5 = _alias_md5;
	if _alias_pk > 0 then
		call GetImportPK(_import_name, _extension, _imp_pk, _ext_pk);
		insert into hacker_import_association (alias_id, import_id, count) values (_alias_pk, _imp_pk, _count)
			on duplicate key update count = count + _count;	
	end if;
END
/MANGINA/
DELIMITER ;
