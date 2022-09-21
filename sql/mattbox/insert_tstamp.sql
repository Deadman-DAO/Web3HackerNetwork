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
	call debug('I think that the update trigger just got called as a result of me modifying the NEW object.');
end
/MANGINA/
DELIMITER ;
