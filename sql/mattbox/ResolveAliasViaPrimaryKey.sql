DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ResolveAliasViaPrimaryKey` (
IN alias_pri_key int(11),
IN in_github_userid char(64)
)
BEGIN
	update alias set github_user_id = in_github_userid where id = alias_pri_key;  
	delete from alias_reserve where alias_id = alias_pri_key;
END
/MANGINA/
DELIMITER ;
