DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ProcessRepoEvalQueue`()
BEGIN
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception occurred in ProcessRepoEvalQueue ',@p1, ':', @p2));
	end;
	
	update repo_eval_queue set xfer = 1;
	
	insert into repo_eval (repo_id, created_at, updated_at, size, watchers, subscribers)
		select r.id, now(), now(), q.repo_size, q.watchers, q.subscribers  from repo_eval_queue q
		join repo r on r.owner = q.owner and r.name = q.name
		left join repo_eval re on re.repo_id = r.id 
		where re.repo_id is NULL and xfer = 1;
	
	delete from repo_eval_queue where xfer = 1;
	
END
/MANGINA/
DELIMITER ;
