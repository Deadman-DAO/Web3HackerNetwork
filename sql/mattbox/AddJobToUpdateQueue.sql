DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`AddJobToUpdateQueue` (
IN machine_name varchar(64),
IN repo_owner varchar(128),
IN repo_name varchar(128)
)
BEGIN
	declare ts datetime default now();
	insert into db_update_queue (tstamp, machine_name, repo_owner, repo_name) select ts, machine_name, repo_owner, repo_name;
END
/MANGINA/
DELIMITER ;
