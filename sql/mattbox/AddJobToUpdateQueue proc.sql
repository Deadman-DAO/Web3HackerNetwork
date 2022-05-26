CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`AddJobToUpdateQueue`(
	in machine_name varchar(64),
	in repo_owner   varchar(128),
	in repo_name    varchar(128)
)
BEGIN
	declare ts datetime default now();
	insert into db_update_queue (tstamp, machine_name, repo_owner, repo_name) select ts, machine_name, repo_owner, repo_name;
END