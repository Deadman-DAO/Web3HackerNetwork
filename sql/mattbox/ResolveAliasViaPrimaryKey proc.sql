CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ResolveAliasViaPrimaryKey`(
	in alias_pri_key int,
	in in_github_userid char(64)
)
BEGIN
	update alias set github_user_id = in_github_userid where id = alias_pri_key;  
END