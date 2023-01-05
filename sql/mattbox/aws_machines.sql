CREATE TABLE `aws_machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `local_ip_addr` varchar(16) DEFAULT NULL,
  `local_ip_str` varchar(24) DEFAULT NULL,
  `extern_ip` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `aws_machine_local_idx` (`local_ip_str`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4