DELIMITER /MANGINA/
create or replace trigger
 
update_tstamp
BEFORE
UPDATE
 on 
hacker_import_association
 for each row 
BEGIN 
	call debug(concat('update_tstamp trigger called for alias ', new.alias_id, ' new id ', new.id));
	set new.tstamp = now(3);
END
/MANGINA/
DELIMITER ;
