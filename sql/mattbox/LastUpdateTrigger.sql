DELIMITER /MANGINA/
create or replace trigger
 
LastUpdateTrigger
BEFORE
UPDATE
 on 
repo
 for each row 
BEGIN 
	set new.last_updated = CURRENT_TIMESTAMP(3); 
END
/MANGINA/
DELIMITER ;
