CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`CreateDBUpdateQueueTable`()
BEGIN
	create table db_update_queue(id int not null auto_increment, tstamp datetime, machine_name varchar(64), repo_owner varchar(128), repo_name varchar(128), primary key (id));
	create table db_update_archive(
		db_update_queue_id int unique not null, 
		reserved datetime, 
		completed datetime, 
		primary key (`db_update_queue_id`), 
		constraint `dua_c` foreign key (db_update_queue_id) references db_update_queue(id)
	);
END