DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateRepoEvalQueueTable`()
BEGIN
	drop table if exists repo_eval_queue;
	create table repo_eval_queue (
		id int unique not null auto_increment primary key,
		owner varchar(128) not null,
		name varchar(128) not null,
		watchers int default 0,
		repo_size int default 0,
		subscribers int default 0,
		inserted_at datetime 
	);
	
END
/MANGINA/
DELIMITER ;
