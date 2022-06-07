CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveRepo`(
in repo_owner varchar(128),
in repo_name varchar(128),
in reserver_id varchar(64),
out success bit
)
BEGIN
	declare ts datetime default now();
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception occurred in ReserveRepo ',@p1, ':', @p2));
		set success = 0;
	end;

	set @repo_id = -1, success = 0;

	select id into @repo_id from repo where owner = repo_owner and name = repo_name;

	if @repo_id > -1 then
		insert into repo_reserve (repo_id, tstamp, reserver) values (@repo_id, ts, reserver_id);
		set success = 1;
	end if; 
END