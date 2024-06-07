-- Check if the migration has already been applied
IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE migration = 'V2__add_website_states') THEN
        
    -- Migration SQL
    USE state_checker;
    CREATE TABLE IF NOT EXISTS `checked_websites` (
        `ID` BIGINT NOT NULL AUTO_INCREMENT,
        `name` TEXT NOT NULL DEFAULT '',
        `state` TEXT NOT NULL DEFAULT '',
        `messageHasBeenSent` TINYINT NOT NULL DEFAULT '0',
        PRIMARY KEY (`ID`)
    ) ENGINE=InnoDB;

    -- Record the migration in schema_migrations table
    INSERT INTO schema_migrations (migration) VALUES ('V2__add_website_states');
END IF;