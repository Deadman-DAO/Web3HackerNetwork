DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateHackerUpdateQueue`()
BEGIN
	drop table if exists hacker_update_queue;
	create table hacker_update_queue(
				id int not null auto_increment primary key,
				md5 char(32),
				name_email varchar(256),
				commit_count int,
				min_date datetime,
				max_date datetime,
				repo_owner varchar(128),
				repo_name  varchar(128),
				commit_array json,
				file_extension varchar(64),
				file_extension_count int,
				import_lang_ext varchar(64),
				import_name varchar(256),
				import_contributions double
	);
END
/MANGINA/
DELIMITER ;
