DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`test_connect_id`()
BEGIN
	SELECT tx.trx_id 
	FROM information_schema.innodb_trx tx
	WHERE tx.trx_mysql_thread_id = connection_id();
END
/MANGINA/
DELIMITER ;
