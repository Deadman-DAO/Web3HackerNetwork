DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`FillRepoJobQueueIfNecessary`()
BEGIN
	declare _current_job_q_size int;
	declare _min_jobs int;
	declare _max_jobs int;
	declare _sleep_time_if_empty_seconds int;
	declare _delay_expiration datetime;
	declare _now datetime default now(3);
	declare _after datetime default now(3);
	declare _randy int default(RAND()*999999999);
	declare _recs_inserted int;
	declare _limit int;
	declare _max_priority_repo_id int;
	declare _exp_date datetime;
	declare _FILL_REPO char(9) default 'FILL_REPO';
	declare _unique_id varchar(32) default LOWER(SUBSTRING(SHA2(RAND(), 512), 1, 32));
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception occurred in FillRepoJobQueueIfNecessary ',@p1, ':', @p2, ' deleting repo_job_q_filler_reservation record (', _randy, ')'));
		delete from repo_job_q_filler_reservation where singleton = 666 and tstamp = _now and ewenique = _randy;
		delete from who_is_boss where task_name = _FILL_REPO and unique_id = _unique_id;
	end;

	select count(*) into _current_job_q_size from staged_repo_job_q srjq;
	select max_jobs, min_jobs, sleep_time_if_empty_seconds, delay_expiration into _max_jobs, _min_jobs, _sleep_time_if_empty_seconds, _delay_expiration from repo_job_q_settings limit 1;
	if _current_job_q_size < _min_jobs and ifnull(_delay_expiration, _now) <= _now THEN 
		select now() + interval 180 second into _exp_date;
		insert ignore into who_is_boss (task_name, expiration_date, unique_id) values (_FILL_REPO, _exp_date, _unique_id);
		if row_count() = 1 then
			/* if 'we' were able to insert that record, then we're responsible to fill the queue.  Anyone else will just exit out. */
			select (_max_jobs - _current_job_q_size) into _limit;
			insert into repo_job_q_filler_reservation values (666, _now, _randy);
			select max(id) + 1 into _max_priority_repo_id from priority_repos;
			insert into staged_repo_job_q (repo_id, tstamp)  
				select X.id, _now from 
				(
				
					select r.id, r.owner, r.name, re.commit_count_last_year , re.size, 
						log(re.commit_count_last_year+1) as log_com, 
						log(1+re.size) as log_size, 
						log(1+re.commit_count_last_year)*log(1+re.size) as priority ,
						RAND() as randy,
						ifnull(pr.id, _max_priority_repo_id) as priority_insert			
						from repo r
						join repo_eval re on re.repo_id = r.id 
						left join repo_reserve rr on rr.repo_id = r.id
						left join staged_repo_job_q srjq on srjq.repo_id = r.id
						left join priority_repos pr on pr.repo_owner = r.owner and pr.repo_name = r.name
						where rr.repo_id is null
						  and srjq.id is null
						  and r.repo_machine_name is NULL 
						  and r.repo_dir is null
						  and r.last_cloned_date is null
						  and r.failed_date is null
						  and re.size is not null
						  and re.size < 800000
						  and re.watchers > 9
				
						order by ifnull(pr.id, _max_priority_repo_id) asc, priority desc
						limit 15000
						
				) as X
				order by X.priority_insert asc, X.randy asc
				limit _limit;		
			
			select row_count() into _recs_inserted;
			if _recs_inserted < 1 then
				update repo_job_q_settings set delay_expiration = now() + interval _sleep_time_if_empty_seconds second;
			else
				update repo_job_q_settings set delay_expiration = null, last_batch_tstamp = _now, last_batch_size_added = _recs_inserted;
			end if;
			select now(3) into _after;
			call debug(concat('FillRepoJobQueueIfNecessary filled ', _recs_inserted, ' records in ', timestampdiff(second, _now, _after)));
			delete from repo_job_q_filler_reservation where singleton = 666 and tstamp = _now and ewenique = _randy;
			delete from who_is_boss where task_name = _FILL_REPO and unique_id = _unique_id;
		end if;

	end if;		
	
END
/MANGINA/
DELIMITER ;
