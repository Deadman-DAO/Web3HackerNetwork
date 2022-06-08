CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`ReserveNextRepoForEvaluation`(
	in who_is_reserving varchar(64)
)
BEGIN
	declare day_millies int default 1000*60*60*24;
	declare _repo_id int;
	declare success bit;
	declare repo_owner varchar(128);
	declare repo_name varchar(128);
	declare _now datetime default CURRENT_TIMESTAMP(3);

	select id, owner, name into _repo_id, repo_owner, repo_name from (
		select r.id, r.owner, r.name, (((max_date - min_date)/day_millies)-((now() - max_date)/day_millies))+commit_count 
		  from repo r
		left join repo_reserve rr on rr.repo_id = r.id
		left join repo_eval re on re.repo_id  = r.id
		where min_date is not null 
		  and rr.repo_id is null 
		  and re.repo_id is null
          and ifnull(r.delay_api_calls_until, _now) <= _now
	      and ifnull(r.retry_count, 0) < 5		  
		order by 4 DESC 
		limit 1
	) as x;

	call reserveRepo(repo_owner, repo_name, who_is_reserving, success);
	if success = 1 then
		select repo_owner, repo_name, _repo_id;
	end if;
	
END