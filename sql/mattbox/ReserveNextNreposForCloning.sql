DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReserveNextNreposForCloning` (
IN _machine_name varchar(128),
IN _max_repos int(11)
)
BEGIN
	declare _dt datetime default current_timestamp(3);

	insert into repo_reserve (repo_id, tstamp, reserver)
		select r.id, _dt, _machine_name
		  from repo r
		join repo_eval re on re.repo_id = r.id
		left join repo_reserve rr on rr.repo_id = r.id
		where rr.repo_id is null
		  and r.repo_machine_name is NULL 
		  and r.repo_dir is null
		  and r.last_cloned_date is null
		order by re.size asc
		limit _max_repos;

	select rr.repo_id, r.owner, r.name 
	  from repo_reserve rr
	  join repo r on r.id = rr.repo_id
	  where rr.reserver = _machine_name
	    and rr.tstamp = _dt;
	
END
/MANGINA/
DELIMITER ;
