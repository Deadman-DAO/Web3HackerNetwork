DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`FillEvalJobQueueIfNecessary`()
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
		call debug(CONCAT('Exception occurred in FillEvalJobQueueIfNecessary ',@p1, ':', @p2, ' deleting eval_job_q_filler_reservation record'));
		delete from eval_job_q_filler_reservation where singleton = 666 and tstamp = _now and ewenique = _randy;
	end;

	select count(*) into _current_job_q_size from staged_eval_job_q srjq;
	select max_jobs, min_jobs, sleep_time_if_empty_seconds, delay_expiration into _max_jobs, _min_jobs, _sleep_time_if_empty_seconds, _delay_expiration from repo_job_q_settings limit 1;
	if _current_job_q_size < _min_jobs and ifnull(_delay_expiration, _now) <= _now THEN 
		select (_max_jobs - _current_job_q_size) into _limit;
		insert into eval_job_q_filler_reservation values (666, _now, _randy);
		/* if we get here, we've inserted the one and only (666) record into the reservation table */
		insert into staged_eval_job_q (repo_id, tstamp)  
			select X.id, _now from 
			(
			
				select r.id, log(1+re.commit_count_last_year)*log(1+re.size) as priority ,
					RAND() as randy from repo r
					left join repo_eval re on re.repo_id = r.id
					left join repo_reserve rr on rr.repo_id = r.id
					left join staged_eval_job_q srjq on srjq.repo_id = r.id
                    where min_date is not null
                      and rr.repo_id is null
                      and re.repo_id is null
                      and ifnull(r.delay_api_calls_until, _now) <= _now
                      and ifnull(r.retry_count, 0) < 5
					order by priority desc
					limit 15000
					
			) as X
			order by X.randy asc
			limit _limit;				
			
		select row_count() into _recs_inserted;
		call debug(concat('FillEvalJobQueueIfNecessary filled ', _recs_inserted, ' records'));
		delete from eval_job_q_filler_reservation where singleton = 666 and tstamp = _now and ewenique = _randy;
	end if;		
	
END
/MANGINA/
DELIMITER ;
