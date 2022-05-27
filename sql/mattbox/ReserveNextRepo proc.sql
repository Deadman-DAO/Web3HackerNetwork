CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveNextRepo`(
in who_is_reserving varchar(64),
out repo_owner varchar(128),
out repo_name varchar(128))
BEGIN
	declare day_millies int default 1000*60*60*24;
	declare repo_id int;
	declare success bit;
	select id, owner, name into repo_id, repo_owner, repo_name from (
		select r.id, r.owner, r.name, (((max_date - min_date)/day_millies)-((now() - max_date)/day_millies))+commit_count 
		  from repo r
		left join repo_reserve rr on rr.repo_id = r.id
		where min_date is not null and rr.repo_id is null
		order by 4 DESC 
		limit 1
	) as x;

	call reserveRepo(repo_owner, repo_name, who_is_reserving, success);
	if success = 0 then
		set repo_owner = null;
		set repo_name = null;
	end if;
	
END