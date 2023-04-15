DROP TABLE IF EXISTS `{0}`;
CREATE TABLE `{0}`
(
    `datetime` varchar(20),
    `open` decimal(10,2),
    `close` decimal(10,2),
    `high` decimal(10,2),
    `low` decimal(10,2),
    `volume` bigint(20),
    `hsl` decimal(12,4),
    `ema5` decimal(12,6),
    `ema12` decimal(12,6),
    `ema26` decimal(12,6),
    `dea4` decimal(12,6),
    `dea9` decimal(12,6),
    `mark` int(11) DEFAULT NULL,
    `klt` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;