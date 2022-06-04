CREATE PROCEDURE w3hacknet.create_repo_table()
BEGIN
	create table repo (
		id int not null auto_increment primary key,
		owner varchar(128) not null,
		name varchar(128) not null,
		commit_count int(11),
		min_date datetime,
		max_date datetime,
		repo_ip_addr varchar(64),
		repo_dir varchar(128),
		numstat_ip_addr varchar(64),
		numstat_dir varchar(128)
	);

END