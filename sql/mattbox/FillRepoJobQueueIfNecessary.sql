DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`FillRepoJobQueueIfNecessary`()
BEGIN
	declare _current_job_q_size int;
	declare _min_jobs int;
	declare _max_jobs int;
	declare _sleep_time_if_empty_seconds int;
	declare _delay_expiration datetime;
	declare _now datetime default now(3);
	declare _randy int default(RAND());
	declare _recs_inserted int;
	declare _limit int;
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception occurred in FillRepoJobQueueIfNecessary ',@p1, ':', @p2, ' deleting repo_job_q_filler_reservation record'));
		delete from repo_job_q_filler_reservation where singleton = 666 and tstamp = _now and ewenique = _randy;
	end;

	select count(*) into _current_job_q_size from staged_repo_job_q srjq;
	select max_jobs, min_jobs, sleep_time_if_empty_seconds, delay_expiration into _max_jobs, _min_jobs, _sleep_time_if_empty_seconds, _delay_expiration from repo_job_q_settings limit 1;
	if _current_job_q_size < _min_jobs and ifnull(_delay_expiration, _now) <= _now THEN 
		select (_max_jobs - _current_job_q_size) into _limit;
		insert into repo_job_q_filler_reservation values (666, _now, _randy);
		
		insert into staged_repo_job_q (repo_id, tstamp)  
			select X.id, _now from 
			(
			
				select r.id, r.owner, r.name, re.commit_count_last_year , re.size, log(re.commit_count_last_year+1) as log_com, log(1+re.size) as log_size, log(1+re.commit_count_last_year)*log(1+re.size) as priority ,
					RAND() as randy from repo r
					join repo_eval re on re.repo_id = r.id 
					left join repo_reserve rr on rr.repo_id = r.id
					left join staged_repo_job_q srjq on srjq.repo_id = r.id
					where rr.repo_id is null
					  and srjq.id is null
					  and r.repo_machine_name is NULL 
					  and r.repo_dir is null
					  and r.last_cloned_date is null
					  and r.failed_date is null
					  and re.size is not null
			
					order by priority desc
					limit 15000
					
			) as X
			order by X.randy asc
			limit _limit;				
			
		select row_count() into _recs_inserted;
		call debug(concat('FillRepoJobQueueIfNecessary filled ', _recs_inserted, ' records'));
		delete from repo_job_q_filler_reservation where singleton = 666 and tstamp = _now and ewenique = _randy;
	end if;		
	
END
/MANGINA/
DELIMITER ;
