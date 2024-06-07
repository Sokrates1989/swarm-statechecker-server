DELIMITER //

CREATE PROCEDURE apply_add_website_states_migration()
BEGIN
    -- Check if the migration has already been applied.
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE migration = 'V2__add_website_states') THEN
            
        -- Migration SQL.
        CREATE TABLE IF NOT EXISTS `checked_websites` (
            `ID` BIGINT NOT NULL AUTO_INCREMENT,
            `name` TEXT NOT NULL,
            `state` TEXT NOT NULL,
            `isDownMessageHasBeenSent` TINYINT NOT NULL DEFAULT '0',
            PRIMARY KEY (`ID`)
        ) ENGINE=InnoDB;

        -- Record the migration in schema_migrations table.
        INSERT INTO schema_migrations (migration) VALUES ('V2__add_website_states');
    END IF;
END//
DELIMITER ;

CALL apply_add_website_states_migration();
DROP PROCEDURE apply_add_website_states_migration;