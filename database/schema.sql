-- schema.sql

-- Enable foreign key constraint enforcement
PRAGMA foreign_keys = ON;

-- Table Definitions

CREATE TABLE Spacecraft (
    SpacecraftID INTEGER PRIMARY KEY,
    COSPAR_ID TEXT,
    NSSDCA_ID TEXT,
    SpacecraftName TEXT NOT NULL,
    LaunchYear INTEGER
);

CREATE TABLE ThermalAnalysisObject (
    ObjectID INTEGER PRIMARY KEY,
    SpacecraftID INTEGER NOT NULL,
    AnalysisObject TEXT NOT NULL,
    FOREIGN KEY (SpacecraftID) REFERENCES Spacecraft (SpacecraftID) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE SoftwareSet (
    SoftwareSetID INTEGER PRIMARY KEY
);
-- SoftwareSet: This table solely defines the existence of a set

CREATE TABLE Software (
    SoftwareID INTEGER PRIMARY KEY,
    SoftwareName TEXT NOT NULL,
    Version TEXT,
    Developer TEXT
);

CREATE TABLE SoftwareSetMembership (
    SoftwareSetID INTEGER NOT NULL,
    SoftwareID INTEGER NOT NULL,
    PRIMARY KEY (SoftwareSetID, SoftwareID),
    FOREIGN KEY (SoftwareSetID) REFERENCES SoftwareSet (SoftwareSetID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (SoftwareID) REFERENCES Software (SoftwareID) ON DELETE RESTRICT ON UPDATE CASCADE -- Consider if software deletion should be restricted if used in a set
);
-- SoftwareSetMembership: This table defines which Software belongs to which Set

CREATE TABLE ReferenceSet (
    ReferenceSetID INTEGER PRIMARY KEY
);
-- ReferenceSet: This table solely defines the existence of a set

CREATE TABLE Reference (
    bibtexkey TEXT PRIMARY KEY,
    Title TEXT,
    Author TEXT,
    etc TEXT -- Stores other BibTeX based info as plain text
);

CREATE TABLE ReferenceSetMembership (
    ReferenceSetID INTEGER NOT NULL,
    bibtexkey TEXT NOT NULL,
    PRIMARY KEY (ReferenceSetID, bibtexkey),
    FOREIGN KEY (ReferenceSetID) REFERENCES ReferenceSet (ReferenceSetID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (bibtexkey) REFERENCES Reference (bibtexkey) ON DELETE RESTRICT ON UPDATE CASCADE -- Consider if reference deletion should be restricted if used in a set
);
-- ReferenceSetMembership: This table defines which Reference belongs to which Set

CREATE TABLE ThermalAnalysisEntry (
    EntryID INTEGER PRIMARY KEY,
    ObjectID INTEGER NOT NULL,
    SoftwareSetID INTEGER NOT NULL,
    ReferenceSetID INTEGER NOT NULL,
    Description TEXT,
    FOREIGN KEY (ObjectID) REFERENCES ThermalAnalysisObject (ObjectID) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (SoftwareSetID) REFERENCES SoftwareSet (SoftwareSetID) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (ReferenceSetID) REFERENCES ReferenceSet (ReferenceSetID) ON DELETE RESTRICT ON UPDATE CASCADE
);