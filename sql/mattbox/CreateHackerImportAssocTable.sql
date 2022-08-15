DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateHackerImportAssocTable`()
BEGIN
	drop table if exists hacker_import_association;

	create table hacker_import_association 
	(
		id int not null auto_increment primary key,
		alias_id int not null references alias(id),
		import_id int not null references source_import(id),
		count float not null default 0.0
	);
	create unique index hacker_import_composite on hacker_import_association(alias_id, import_id);
END
/MANGINA/
DELIMITER ;
