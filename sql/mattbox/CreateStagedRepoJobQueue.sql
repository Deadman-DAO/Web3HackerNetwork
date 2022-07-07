DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateStagedRepoJobQueue`
BEGIN
	drop table if exists staged_repo_job_q;

	create table staged_repo_job_q (
		id int not null auto_increment primary key,
		repo_id int unique not null references repo(id),
		tstamp datetime);
	
	drop table if exists repo_job_q_settings;
	create table repo_job_q_settings (
		max_jobs int not null ,
		min_jobs int not null ,
		sleep_time_if_empty_seconds int,
		last_batch_size_added int not null ,
		last_batch_tstamp datetime,
		delay_expiration datetime
	);

	drop table if exists repo_job_q_filler_reservation;
	create table repo_job_q_filler_reservation (
		singleton int unique not null default(666),
		tstamp datetime not null,
		ewenique int not null
	);
	
	drop table if exists rediculous_fucking_work_around;
	create table rediculous_fucking_work_around (
		connection_id int unique not null primary key,
		repo_id int not null,
		transaction_id int,
		tstamp datetime
	);
	insert into repo_job_q_settings values (500, 75, 59, -1, null, null);
END
/MANGINA/
DELIMITER ;
