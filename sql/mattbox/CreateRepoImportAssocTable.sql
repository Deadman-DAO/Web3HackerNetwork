DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateRepoImportAssocTable`()
BEGIN
	drop table if exists repo_import_association;

	create table repo_import_association 
	(
		id int not null auto_increment primary key,
		repo_id int not null references repo(id),
		import_id int not null references source_import(id),
		count int not null default 0
	);
	create unique index repo_import_composite on repo_import_association(repo_id, import_id);
END
/MANGINA/
DELIMITER ;
