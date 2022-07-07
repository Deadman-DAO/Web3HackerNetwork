DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ResolveAlias` (
IN alias_hash char(32),
IN in_github_userid char(64)
)
BEGIN
	update alias set github_user_id = in_github_userid where md5 = alias_hash;  
END
/MANGINA/
DELIMITER ;
