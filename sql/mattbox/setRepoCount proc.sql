CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`setRepoCount`(
in owner_name varchar(128),
in repo_name varchar(128),
in ref_commit_count int)
BEGIN
	update ignore repo set commit_count = ref_commit_count where owner = owner_name and name = repo_name;
END