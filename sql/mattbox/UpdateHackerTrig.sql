DELIMITER /MANGINA/
create or replace trigger
 
UpdateHackerTrig
AFTER
INSERT
 on 
hacker_update_queue
 for each row 
begin 
	call UpdateHacker(new.md5, new.name_email, new.commit_count, new.min_date, new.max_date, new.repo_owner, new.repo_name, new.commit_array, 
					  new.file_extension, new.file_extension_count, new.import_lang_ext, new.import_name, new.import_contributions);

end
/MANGINA/
DELIMITER ;
