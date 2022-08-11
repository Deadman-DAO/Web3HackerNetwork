DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateRepoEvalTable`()
BEGIN
	drop table if exists repo_eval;

	create table repo_eval
	(
		repo_id int unique not null, 
		created_at datetime, 
		updated_at datetime, 
		pushed_at datetime, 
		homepage varchar(128), 
		size int, 
		watchers int, 
		contributor_count int, 
		contributor_sum int, 
		commit_count_last_year int,
		parallel_repo_count int,
		primary key (`repo_id`), 
		foreign key (repo_id) references repo(id)
	);	
END
/MANGINA/
DELIMITER ;
