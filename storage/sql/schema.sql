CREATE DATABASE IF NOT EXISTS agu DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS agu_30 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS agu_00 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS agu_60 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE DATABASE IF NOT EXISTS agu_51 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

USE agu;
CREATE TABLE IF NOT EXISTS `code_dict` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(20) NOT NULL,
  `status` int(11) DEFAULT '0',
  `created` datetime DEFAULT NULL,
  `updated` datetime NOT NULL DEFAULT '1900-01-01 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

USE agu;
CREATE TABLE IF NOT EXISTS `reverse_signal` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `stock_code` varchar(20) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `reverse_type` varchar(20) DEFAULT NULL,
  `reverse_datetime` varchar(20) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

USE agu;
CREATE TABLE IF NOT EXISTS `watcher` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `code` varchar(20) DEFAULT NULL,
  `klt` int(11) DEFAULT NULL,
  `last_reverse_bottom` datetime DEFAULT NULL,
  `last_reverse_top` datetime DEFAULT NULL,
  `last_macd_balance` datetime DEFAULT NULL,
  `last_bottom` datetime DEFAULT NULL,
  `last_top` datetime DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
