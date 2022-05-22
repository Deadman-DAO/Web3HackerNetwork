CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ResolveAlias`(
in alias_hash char(32),
in in_github_userid char(64)
)
BEGIN
	update alias set github_user_id = in_github_userid where md5 = alias_hash;  
END