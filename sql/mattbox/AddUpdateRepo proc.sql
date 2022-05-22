CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`addUpdateRepo`(
in owner_name varchar(128),
in repo_name varchar(128),
out success bit)
BEGIN
	insert ignore into repo (owner, name) select owner_name, repo_name;
	select row_count() into success;
END