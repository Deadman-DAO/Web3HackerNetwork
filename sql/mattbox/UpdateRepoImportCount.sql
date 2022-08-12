DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`UpdateRepoImportCount` (
IN _repo_pk int(11),
IN _import_name varchar(256),
IN _extension varchar(64),
IN _count int(11)
)
BEGIN
	declare _ext_pk int;
	declare _imp_pk int;
	call GetImportPK(_import_name, _extension, _imp_pk, _ext_pk);
	insert into repo_import_association (repo_id, import_id, count) values (_repo_pk, _imp_pk, _count)
		on duplicate key update count = count + _count;
END
/MANGINA/
DELIMITER ;
