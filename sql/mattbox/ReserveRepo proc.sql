CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveRepo`(
in repo_owner varchar(128),
in repo_name varchar(128),
in reserver_id varchar(64),
out success bit
)
BEGIN
	declare ts datetime default now();
	set @repo_id = -1, success = 0;
#	call debug(concat(repo_owner, repo_name, reserver_id));
	select id into @repo_id from repo where owner = repo_owner and name = repo_name;
#	call debug(concat('Repo ID = ',@repo_id));
	if @repo_id > -1 then
		insert ignore into repo_reserve (repo_id, tstamp, reserver) values (@repo_id, ts, reserver_id);
		if row_count() > 0 then
			set success = 1;
		end if;
	end if; 
END