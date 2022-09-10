DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateImportTrackingTables`()
BEGIN
	drop table if exists import_performance_tracking;

	create table import_performance_tracking
		(
			id int not null auto_increment primary key,
			repo_id int(11),
			success bit(1),
			stats_json longblob,	
			starttime datetime, 
			endtime datetime,
			hacker_name_map_size int,
			hacker_name_map_completion datetime,
			extension_map_size int,
			extension_map_completion datetime,
			import_map_map_size int,
			import_map_map_completion datetime,
			hacker_extension_map_size int,
			hacker_extension_map_completion datetime,
			foreign key (repo_id) references repo(id)
		);
END
/MANGINA/
DELIMITER ;
