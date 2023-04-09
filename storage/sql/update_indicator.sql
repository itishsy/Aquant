UPDATE `{0}`
SET `ema5` = %s,
    `ema12` = %s,
    `ema26` = %s,
    `dea4` = %s,
    `dea9` = %s,
    `mark` = %s
WHERE `datetime` = %s AND `klt` = {1} ;