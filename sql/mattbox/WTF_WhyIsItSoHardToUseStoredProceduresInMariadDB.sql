DELIMITER /MANGINA/
create or replace trigger
 
WTF_WhyIsItSoHardToUseStoredProceduresInMariadDB
AFTER
DELETE
 on 
staged_repo_job_q
 for each row 
BEGIN 
	declare _tx_id int default(-1);
	
	SELECT tx.trx_id into _tx_id
	FROM information_schema.innodb_trx tx
	WHERE tx.trx_mysql_thread_id = connection_id();

	replace into rediculous_fucking_work_around (connection_id, repo_id, transaction_id, tstamp)
		select connection_id(), OLD.repo_id, _tx_id, now(3);
END
/MANGINA/
DELIMITER ;
