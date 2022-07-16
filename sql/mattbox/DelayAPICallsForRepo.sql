DELIMITER /MANGINA/
create or replace procedure `w3hacknet`.`DelayAPICallsForRepo` (
IN _repo_id int(11)
)
BEGIN
	update repo set delay_api_calls_until = TIMESTAMPADD(MINUTE, 2,  CURRENT_TIMESTAMP(3) ), retry_count = ifnull(retry_count, 0) + 1
	 where id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;
END
/MANGINA/
DELIMITER ;
