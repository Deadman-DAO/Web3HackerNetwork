DELIMITER /MANGINA/
create or replace trigger
 
insert_tstamp
BEFORE
INSERT
 on 
hacker_import_association
 for each row 
begin
	call debug(concat('insert_tstamp trigger called for alias ', new.alias_id, ' new id ', new.id));
	set new.tstamp = now(3);
end
/MANGINA/
DELIMITER ;
