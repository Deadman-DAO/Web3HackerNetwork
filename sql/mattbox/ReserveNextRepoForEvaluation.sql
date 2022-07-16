DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`ReserveNextRepoForEvaluation` (
IN _who_is_reserving varchar(64)
)
BEGIN
	declare _repo_owner varchar(128);
	declare _repo_name varchar(128);
	declare _repo_id int(11);
	/* Add error-handler just to make sure that we clean up the rfwa table */
	declare exit handler for SQLEXCEPTION
	begin
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
		call debug(CONCAT('Exception occurred in ReserveNextRepoForEVAL ',@p1, ':', @p2));
		delete from rediculous_fucking_work_around where connection_id = connection_id();
	end;

	/* clear out variables to ensure detecting success/failure */
	select -1, null, null into _repo_id, _repo_owner, _repo_name;

	/* fill up the queue if necessary */
	call FillEvalJobQueueIfNecessary();

	/* OK.  Here's the work around:
	 * Delete a record from the staged queue.
	 * There's a post-delete trigger on that table which will use the current connection_id bound to this transaction to store the repo_id in the rfwa table 
	 */
	delete from staged_eval_job_q 
		order by id
		limit 1;
	/* Now pull the value stored by the trigger out of the rfwa table */
	select repo_id into _repo_id from rediculous_fucking_work_around where connection_id = connection_id();

	/* Make sure and delete any records bound to this connection id */
	delete from rediculous_fucking_work_around where connection_id = connection_id();

	/* Now if we actually got a repo_id we go ahead and insert a repo_reseve record and return back the owner/name/id set */
	if _repo_id > 0 then
		insert into repo_reserve (repo_id, tstamp, reserver) values (_repo_id, now(3), _who_is_reserving);
		select owner, name into _repo_owner, _repo_name from repo where id = _repo_id;
	end if; 
		
	select _repo_owner, _repo_name, _repo_id;
	

END
/MANGINA/
DELIMITER ;
