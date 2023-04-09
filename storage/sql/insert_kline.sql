INSERT INTO `{0}`(`datetime`, `open`, `close`, `high`, `low`, `volume`, `klt`)
SELECT %s, %s, %s, %s, %s, %s, {1}
FROM DUAL WHERE NOT EXISTS(
    SELECT 1
    FROM `{0}`
    WHERE `datetime` = %s AND `klt` = {1}
    );