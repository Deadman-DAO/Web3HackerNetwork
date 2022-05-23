CREATE DEFINER=`matt`@`localhost` PROCEDURE `w3hacknet`.`CreateRepoReserveTable`()
BEGIN
	drop table if exists repo_reserve;

	create table repo_reserve 
		(
			repo_id int unique not null, 
			tstamp datetime, 
			reserver varchar(128), 
			primary key (`repo_id`), 
			foreign key (repo_id) references repo(id)
		);
	
END