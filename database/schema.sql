-- schema.sql

-- Enable foreign key constraint enforcement
PRAGMA foreign_keys = ON;

-- Table Definitions

CREATE TABLE spacecraft (
    spacecraft_id INTEGER PRIMARY KEY,
    cospar_id TEXT,
    spacecraft_name TEXT NOT NULL,
    launch_year INTEGER,
    spacecraft_description TEXT
);

CREATE TABLE thermal_analysis_object (
    object_id INTEGER PRIMARY KEY,
    spacecraft_id INTEGER NOT NULL,
    analysis_object TEXT NOT NULL,
    FOREIGN KEY (spacecraft_id) REFERENCES spacecraft (spacecraft_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE software_set (
    software_set_id INTEGER PRIMARY KEY
);
-- software_set: This table solely defines the existence of a set

CREATE TABLE software (
    software_id INTEGER PRIMARY KEY,
    software_name TEXT NOT NULL,
    software_version TEXT,
    developer TEXT
);

CREATE TABLE software_set_membership (
    software_set_id INTEGER NOT NULL,
    software_id INTEGER NOT NULL,
    PRIMARY KEY (software_set_id, software_id),
    FOREIGN KEY (software_set_id) REFERENCES software_set (software_set_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (software_id) REFERENCES software (software_id) ON DELETE RESTRICT ON UPDATE CASCADE -- Consider if software deletion should be restricted if used in a set
);
-- software_set_membership: This table defines which software belongs to which set

CREATE TABLE reference_set (
    reference_set_id INTEGER PRIMARY KEY
);
-- reference_set: This table solely defines the existence of a set

CREATE TABLE reference (
    bibtex_key TEXT PRIMARY KEY,
    document_type TEXT,
    title TEXT,
    author TEXT,
    journal TEXT,
    doi TEXT,
    book_title TEXT,
    publication_year INTEGER
);

CREATE TABLE reference_set_membership (
    reference_set_id INTEGER NOT NULL,
    bibtex_key TEXT NOT NULL,
    PRIMARY KEY (reference_set_id, bibtex_key),
    FOREIGN KEY (reference_set_id) REFERENCES reference_set (reference_set_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bibtex_key) REFERENCES reference (bibtex_key) ON DELETE RESTRICT ON UPDATE CASCADE -- Consider if reference deletion should be restricted if used in a set
);
-- reference_set_membership: This table defines which reference belongs to which set

CREATE TABLE thermal_analysis_entry (
    entry_id INTEGER PRIMARY KEY,
    object_id INTEGER NOT NULL,
    software_set_id INTEGER NOT NULL,
    reference_set_id INTEGER NOT NULL,
    thermal_description TEXT,
    FOREIGN KEY (object_id) REFERENCES thermal_analysis_object (object_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (software_set_id) REFERENCES software_set (software_set_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (reference_set_id) REFERENCES reference_set (reference_set_id) ON DELETE RESTRICT ON UPDATE CASCADE
);