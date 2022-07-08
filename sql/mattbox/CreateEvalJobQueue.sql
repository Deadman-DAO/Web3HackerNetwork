DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateEvalJobQueue`()
BEGIN
    drop table if exists staged_eval_job_q;

    create table staged_eval_job_q (
                                       id int not null auto_increment primary key,
                                       repo_id int unique not null references repo(id),
                                       tstamp datetime);

    drop table if exists eval_job_q_settings;
    create table eval_job_q_settings (
                                         max_jobs int not null ,
                                         min_jobs int not null ,
                                         sleep_time_if_empty_seconds int,
                                         last_batch_size_added int not null ,
                                         last_batch_tstamp datetime,
                                         delay_expiration datetime
    );

    drop table if exists eval_job_q_filler_reservation;
    create table eval_job_q_filler_reservation (
                                                   singleton int unique not null default(666),
                                                   tstamp datetime not null,
                                                   ewenique int not null
    );

    insert into eval_job_q_settings values (500, 75, 59, -1, null, null);
END
/MANGINA/
DELIMITER ;
