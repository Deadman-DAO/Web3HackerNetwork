CREATE TABLE `commit_check` (
  `commit_hash` char(40) DEFAULT NULL,
  `machine_name` char(48) DEFAULT NULL,
  `is_new` bit(1) DEFAULT b'0',
  KEY `cc_mac_com` (`machine_name`,`commit_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4