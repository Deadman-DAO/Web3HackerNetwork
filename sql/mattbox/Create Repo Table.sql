CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`create_repo_table`()
BEGIN
	create table repo (
		id int not null auto_increment primary key,
		owner varchar(128) not null,
		name varchar(128) not null,
		commit_count int(11),
		min_date datetime,
		max_date datetime,
		last_cloned_date datetime default null,
		last_numstat_date datetime default null,
		last_analysis_date datetime default null,
		repo_machine_name varchar(64),
		repo_dir varchar(128),
		numstat_machine_name varchar(64),
		numstat_dir varchar(128)
	);

END