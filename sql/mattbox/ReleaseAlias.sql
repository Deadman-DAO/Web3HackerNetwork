DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReleaseAlias` (
IN _alias_md5 char(32),
IN _commit_count int(11)
)
BEGIN
	declare _alias_id int default -1;
	declare _td datetime default current_timestamp(3);
	select id into _alias_id from alias where md5 = _alias_md5;
	if _alias_id > 0 then
		delete from alias_reserve where alias_id = _alias_id;
		update alias set count = _commit_count, last_traced = _td where id = _alias_id;
	end if;
END
/MANGINA/
DELIMITER ;
