CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tstamp` datetime(3) DEFAULT NULL,
  `message` varchar(2048) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2630281 DEFAULT CHARSET=utf8mb4