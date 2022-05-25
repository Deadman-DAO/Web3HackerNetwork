CREATE PROCEDURE w3hacknet.CreateDBUpdateQueueTable()
BEGIN
	create table db_update_queue(id int not null auto_increment, tstamp datetime, machine_name varchar(64), repo_owner varchar(128), repo_name varchar(128), primary key (id));
END