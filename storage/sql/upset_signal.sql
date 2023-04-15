INSERT INTO `reverse_signal`(`stock_code`, `level`,`reverse_type`,`reverse_datetime`,`created`)
SELECT %s, %s, %s, %s, %s, %s, {1}
FROM DUAL WHERE NOT EXISTS(
    SELECT 1
    FROM `{0}`
    WHERE `datetime` = %s AND `klt` = {1}
    );