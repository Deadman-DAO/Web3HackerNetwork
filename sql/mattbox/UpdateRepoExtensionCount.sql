DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`UpdateRepoExtensionCount` (
IN _repo_pk int(11),
IN _extension varchar(64),
IN _count int(11)
)
BEGIN
	declare _ext_pk int;
	call GetFileExtensionPK(_extension, _ext_pk);
	insert into repo_extension_association (repo_id, extension_id, count) values (_repo_pk, _ext_pk, _count)
		on duplicate key update count = count + _count;
END
/MANGINA/
DELIMITER ;
