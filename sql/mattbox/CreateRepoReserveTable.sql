DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateRepoReserveTable`()
BEGIN
	drop table if exists repo_reserve;

	create table repo_reserve 
		(
			id int not null auto_increment primary key,
			repo_id int unique not null, 
			tstamp datetime, 
			reserver varchar(128), 
			foreign key (repo_id) references repo(id)
		);
	
END
/MANGINA/
DELIMITER ;
