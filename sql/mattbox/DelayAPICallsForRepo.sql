CREATE PROCEDURE w3hacknet.DelayAPICallsForRepo(in _repo_id int)
BEGIN
	update repo set delay_api_calls_until = TIMESTAMPADD(MINUTE, 2,  CURRENT_TIMESTAMP(3) )
	 where id = _repo_id;
	delete from repo_reserve where repo_id = _repo_id;
END