-- import_data.sql

-- Set mode to CSV for robust handling of quoting and commas
.mode csv

-- Optional: Explicitly set separator if not comma
-- .separator ","

-- Import data into each table
-- IMPORTANT: CSVs are assumed to have NO header row and columns in the correct order.

.print "Importing Spacecraft..."
.import spacecraft.csv Spacecraft

.print "Importing Software..."
.import software.csv Software

.print "Importing Reference..."
.import reference.csv Reference

.print "Importing ThermalAnalysisObject..."
.import thermal_analysis_object.csv ThermalAnalysisObject

-- Import Set definition tables (assuming CSVs contain the Set IDs)
.print "Importing SoftwareSet..."
.import software_set.csv SoftwareSet

.print "Importing ReferenceSet..."
.import reference_set.csv ReferenceSet

-- Import membership tables (CSVs must contain correct FK IDs)
.print "Importing SoftwareSetMembership..."
.import software_set_membership.csv SoftwareSetMembership

.print "Importing ReferenceSetMembership..."
.import reference_set_membership.csv ReferenceSetMembership

-- Import the main entry table (CSV must contain correct FK IDs)
.print "Importing ThermalAnalysisEntry..."
.import thermal_analysis_entry.csv ThermalAnalysisEntry

.print "Import complete."

-- Optional: Optimize the database file after import
VACUUM;