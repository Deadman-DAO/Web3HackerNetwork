DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`CreateImportTable`()
BEGIN
	drop table if exists source_import;

	create table source_import (
		id int not null auto_increment primary key,
		name varchar(256) not null,
		extension_id int not null references file_extension,
		parent_import int references source_port.id);

END
/MANGINA/
DELIMITER ;
