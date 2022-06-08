CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`CreateHackerUpdateQueue`()
BEGIN
	drop table if exists hacker_update_queue;
	create table hacker_update_queue(
				id int not null auto_increment primary key,
				md5 char(32),
				name_email varchar(256),
				commit_count int,
				min_date datetime,
				max_date datetime,
				commit_array json,
				completed bit default 0);
END