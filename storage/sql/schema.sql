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
  `updated` datetime DEFAULT NULL,
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
  `watch_klt` varchar(100) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

USE agu;
CREATE TABLE `watcher_detail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `watcher_id` int(11) NOT NULL,
  `code` varchar(20) DEFAULT NULL,
  `klt` int(11) DEFAULT NULL,
  `event_type` varchar(100) DEFAULT NULL,
  `event_datetime` varchar(100) DEFAULT NULL,
  `notify` int(11) DEFAULT '0',
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

