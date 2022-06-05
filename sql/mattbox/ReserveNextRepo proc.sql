CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveNextRepo`(
in who_is_reserving varchar(64),
out repo_owner varchar(128),
out repo_name varchar(128),
out _repo_id int)
BEGIN
	declare day_millies int default 1000*60*60*24;
	declare success bit;
	select id, owner, name into _repo_id, repo_owner, repo_name from (
		select r.id, r.owner, r.name, 
			(((((re.pushed_at  - re.created_at)/day_millies)-((now() - re.pushed_at)/day_millies))+commit_count)/(re.parallel_repo_count+1))+commit_count_last_year
		  from repo r
		join repo_eval re on re.repo_id = r.id
		left join repo_reserve rr on rr.repo_id = r.id
		where rr.repo_id is null
		  and r.repo_machine_name is NULL 
		  and r.repo_dir is null
		  and r.last_cloned_date is null
		order by 4 DESC 
		limit 1
	) as x;

	call reserveRepo(repo_owner, repo_name, who_is_reserving, success);
	if success = 0 then
		set repo_owner = null;
		set repo_name = null;
		set _repo_id = -1;
	end if;
	
END