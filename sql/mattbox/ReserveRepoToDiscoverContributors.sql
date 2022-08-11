DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReserveRepoToDiscoverContributors` (
IN _reserver_user_id varchar(32)
)
BEGIN
	declare _owner varchar(128);
	declare _name varchar(128);
	declare _repo_id int;
	declare success bit;
	declare _now datetime default CURRENT_TIMESTAMP(3);

	select r.id, r.owner, r.name from repo r
		left join repo_reserve rr on rr.repo_id = r.id 
		join repo_eval re on re.repo_id = r.id 
		where rr.repo_id is null and re.repo_id  is not null and re.contributor_count is NULL 
		   and ifnull(r.delay_api_calls_until, _now) <= _now
		   and ifnull(r.retry_count, 0) < 5
		limit 1;
	
	call reserveRepo(_owner, _name, _reserver_user_id, success);
	if success = 1 then
		select _repo_id, _owner, _name;
	end if;
	

END
/MANGINA/
DELIMITER ;
