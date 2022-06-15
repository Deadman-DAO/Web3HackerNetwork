CREATE DEFINER=`matt`@`localhost` TRIGGER LastUpdateTrigger
BEFORE update
ON repo FOR EACH ROW
BEGIN 
	set new.last_updated = CURRENT_TIMESTAMP(3); 
END