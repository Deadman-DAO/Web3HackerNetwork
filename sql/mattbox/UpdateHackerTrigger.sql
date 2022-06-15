CREATE DEFINER=`matt`@`localhost` TRIGGER UpdateHackerTrigger
AFTER INSERT
ON hacker_update_queue FOR EACH ROW
BEGIN 
	call UpdateHacker(new.md5, new.name_email, new.commit_count, new.min_date, new.max_date, new.repo_owner, new.repo_name, new.commit_array);
end