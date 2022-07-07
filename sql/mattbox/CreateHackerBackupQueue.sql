	drop table if exists hacker_update_backup;
	create table hacker_update_backup(
				id int not null auto_increment primary key,
				md5 char(32),
				name_email varchar(256),
				commit_count int,
				min_date datetime,
				max_date datetime,
				repo_owner varchar(128),
				repo_name  varchar(128),
				commit_array json);
END