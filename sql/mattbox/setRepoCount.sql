DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`setRepoCount` (
IN owner_name varchar(128),
IN repo_name varchar(128),
IN ref_commit_count int(11)
)
BEGIN
	update ignore repo set commit_count = ref_commit_count where owner = owner_name and name = repo_name;
END
/MANGINA/
DELIMITER ;
