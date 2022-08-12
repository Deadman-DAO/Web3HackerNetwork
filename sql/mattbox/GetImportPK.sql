DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`GetImportPK` (
IN _name varchar(256),
IN _file_extension varchar(64),
OUT _import_pk int(11),
OUT _ext_pk int(11)
)
BEGIN
	set _import_pk = -1;
	call GetFileExtensionPK(_file_extension, _ext_pk);
	select id into _import_pk from source_import si where si.name = _name;
	if _import_pk < 1 then	
		insert into source_import (name, extension_id) values (_name, _extPK);
		select LAST_INSERT_ID() into _import_pk;  
	end if;
END
/MANGINA/
DELIMITER ;
