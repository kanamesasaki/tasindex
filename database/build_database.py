import sqlite3
import csv
import os
import sys
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from collections import defaultdict

# --- Configuration ---
INPUT_CSV_FILE = 'tasindex_import.csv' # Your input CSV file with bibtex keys
BIBTEX_FILE = 'references.bib'          # Your BibTeX file <--- NEW
DB_FILE = 'spacecraft_thermal.db'       # Output SQLite database file
SCHEMA_FILE = 'schema.sql'              # Database schema definition
# --- End Configuration ---

def init_db():
    """Initializes the database: deletes old file and creates tables from schema."""
    print(f"Initializing database '{DB_FILE}'...")
    if os.path.exists(DB_FILE):
        print(f"  Removing existing database file.")
        os.remove(DB_FILE)

    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file '{SCHEMA_FILE}' not found.")
        sys.exit(1)

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"  Executing schema from '{SCHEMA_FILE}'...")
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)

        print("  Ensuring reference_set ID 0 exists for 'No References'.")
        cursor.execute("INSERT OR IGNORE INTO reference_set (reference_set_id) VALUES (0)")

        conn.commit()
        print("Database initialized successfully.")
        return True # Indicate success
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def populate_references_from_bibtex(bib_file_path):
    """Parses a BibTeX file and populates the reference table."""
    print(f"Populating references from '{bib_file_path}'...")
    if not os.path.exists(bib_file_path):
        print(f"Warning: BibTeX file '{bib_file_path}' not found. Reference details will be empty.")
        return set() # Return empty set if file not found

    inserted_keys = set()
    conn = None # Initialize conn to None
    try:
        with open(bib_file_path, 'r', encoding='utf-8') as bibfile:
            # Configure parser
            parser = BibTexParser(common_strings=True)
            parser.customization = convert_to_unicode
            parser.ignore_nonstandard_types = False # Try to parse even non-standard types
            parser.homogenize_fields = True # e.g. map 'Key' to 'keyword'

            bib_database = bibtexparser.load(bibfile, parser=parser)

        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        for entry in bib_database.entries:
            bib_key = entry.get('ID')
            if not bib_key:
                print(f"  Skipping entry with no ID: {entry}")
                continue

            # 変更: BibTeXのエントリタイプを document_type として取得
            document_type = entry.get('ENTRYTYPE', '').lower()  # 小文字に統一
            
            title = entry.get('title', '')
            author = entry.get('author', '')
            journal = entry.get('journal', '')
            doi = entry.get('doi', '')
            book_title = entry.get('booktitle', '')
            year = entry.get('year', '')
            
            try:
                publication_year = int(year) if year else None
            except ValueError:
                print(f"  Warning: Invalid year value '{year}' for entry {bib_key}, setting to NULL")
                publication_year = None

            # SQL文も更新
            print(f"  Adding/Updating Reference: {bib_key} (Type: {document_type})")
            cursor.execute(
                """
                INSERT OR REPLACE INTO reference 
                (bibtex_key, document_type, title, author, journal, doi, book_title, publication_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (bib_key, document_type, title, author, journal, doi, book_title, publication_year)
            )
            inserted_keys.add(bib_key)

        conn.commit()
        print(f"Successfully processed {len(inserted_keys)} references from BibTeX file.")
        return inserted_keys

    except FileNotFoundError:
        print(f"Warning: BibTeX file '{bib_file_path}' not found. Reference details will be empty.")
        return set() # Return empty set
    except Exception as e: # Catch broader parsing errors
        print(f"Error processing BibTeX file '{bib_file_path}': {e}")
        # Optionally raise error or return empty set depending on desired behavior
        # raise # Stop execution
        return set() # Continue without BibTeX data
    finally:
        if conn:
            conn.close()


def process_data(valid_bibtex_keys):
    """Reads the input CSV and populates the database, using pre-loaded references."""
    print(f"Processing data from '{INPUT_CSV_FILE}'...")

    if not os.path.exists(INPUT_CSV_FILE):
        print(f"Error: Input CSV file '{INPUT_CSV_FILE}' not found.")
        sys.exit(1)

    # Caches (Reference cache no longer needed to insert, just to validate keys)
    spacecraft_cache = {}
    object_cache = {}
    software_cache = {}
    software_set_cache = {}
    reference_set_cache = {}
    # reference_cache = valid_bibtex_keys # Use the set passed from bibtex processing

    conn = None # Initialize conn
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        with open(INPUT_CSV_FILE, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            entry_count = 0
            skipped_rows = 0
            for row_num, row in enumerate(reader, start=2):
                entry_count += 1
                print(f"\nProcessing Row {row_num}: {row.get('Spacecraft_Name', 'N/A')}")
                try:
                    # --- 1. Get/Create Spacecraft ---
                    cospar_id = row.get('cospar_id', '').strip()
                    sc_name = row.get('spacecraft_name', '').strip()
                    spacecraft_description = row.get('spacecraft_description', '').strip()

                    launch_year_str = row.get('launch_year', '').strip()
                    launch_year = None
                    if launch_year_str:
                        try:
                            launch_year = int(launch_year_str)
                        except ValueError:
                            print(f"  Warning: Invalid launch_year value '{launch_year_str}', setting to NULL")

                    sc_key = (cospar_id, sc_name)
                    if not sc_name:
                         print(f"  Skipping row {row_num}: Missing Spacecraft Name.")
                         skipped_rows += 1
                         continue
                    if sc_key not in spacecraft_cache:
                        cursor.execute(
                            "INSERT INTO spacecraft (cospar_id, spacecraft_name, launch_year, spacecraft_description) VALUES (?, ?, ?, ?)", 
                            (cospar_id, sc_name, launch_year, spacecraft_description)
                        )
                        spacecraft_id = cursor.lastrowid
                        spacecraft_cache[sc_key] = spacecraft_id
                        print(f"  Creating Spacecraft: {sc_name} ({cospar_id}), launch year: {launch_year or 'N/A'} -> ID {spacecraft_id}")
                    else:
                        spacecraft_id = spacecraft_cache[sc_key]
                        print(f"  Found Spacecraft: ID {spacecraft_id}")


                    # --- 2. Get/Create Analysis Object ---
                    object_name = row.get('analysis_object', '').strip()
                    if not object_name or object_name.lower() == 'system':
                        object_name = "System"
                    obj_key = (spacecraft_id, object_name)
                    if obj_key not in object_cache:
                        cursor.execute("INSERT INTO thermal_analysis_object (spacecraft_id, analysis_object) VALUES (?, ?)", obj_key)
                        object_id = cursor.lastrowid
                        object_cache[obj_key] = object_id
                        print(f"  Creating Object: {object_name} -> ID {object_id}")
                    else:
                        object_id = object_cache[obj_key]
                        print(f"  Found Object: ID {object_id}")


                    # --- 3. Get/Create Software & Build Software Set ---
                    current_software_ids = set()
                    for i in range(1, 6):
                        sw_name = row.get(f'software_{i}', '').strip()
                        sw_version = row.get(f'version_{i}', '').strip() or None
                        if sw_name:
                            print(f"  Processing Software: {sw_name} (Version: {sw_version or 'N/A'})")
                            if sw_name not in software_cache:
                                cursor.execute("SELECT software_id FROM software WHERE software_name = ?", (sw_name,))
                                existing = cursor.fetchone()
                                if not existing:
                                    cursor.execute("INSERT INTO software (software_name, software_version) VALUES (?, ?)", (sw_name, sw_version))
                                    sw_id = cursor.lastrowid
                                    print(f"    Creating Software Entry -> ID {sw_id}")
                                else:
                                    sw_id = existing[0]
                                    print(f"    Found existing Software ID: {sw_id}")
                                software_cache[sw_name] = sw_id
                            else:
                                sw_id = software_cache[sw_name]
                                print(f"    Found cached Software ID: {sw_id}")
                            current_software_ids.add(sw_id)

                    frozen_sw_ids = frozenset(current_software_ids)
                    if not frozen_sw_ids:
                         cursor.execute("INSERT OR IGNORE INTO software_set (software_set_id) VALUES (0)") # Ensure Set 0 exists
                         sw_set_id = 0
                         print(f"  Warning: No software found. Assigning software_set ID {sw_set_id}.")
                    elif frozen_sw_ids not in software_set_cache:
                        cursor.execute("INSERT INTO software_set DEFAULT VALUES")
                        sw_set_id = cursor.lastrowid
                        software_set_cache[frozen_sw_ids] = sw_set_id
                        print(f"  Creating new software_set ID: {sw_set_id} for { {id for id in frozen_sw_ids} }")
                        for sw_id in frozen_sw_ids:
                            cursor.execute("INSERT INTO software_set_membership (software_set_id, software_id) VALUES (?, ?)", (sw_set_id, sw_id))
                    else:
                        sw_set_id = software_set_cache[frozen_sw_ids]
                        print(f"  Found existing software_set ID: {sw_set_id}")


                    # --- 4. Get References & Build Reference Set ---
                    current_ref_keys = set()
                    for i in range(1, 4):
                        ref_key = row.get(f'reference_{i}', '').strip()
                        if ref_key:
                            # Check if the key exists in the set populated from BibTeX
                            if ref_key not in valid_bibtex_keys:
                                print(f"  Warning: BibTeX key '{ref_key}' found in CSV but not in '{BIBTEX_FILE}'. Skipping reference linkage for this key.")
                            else:
                                print(f"  Processing Reference Link: {ref_key}")
                                current_ref_keys.add(ref_key) # Only add valid keys

                    # Create/Find Reference Set
                    frozen_ref_keys = frozenset(current_ref_keys)
                    if not frozen_ref_keys:
                         ref_set_id = 0 # Use pre-defined set for "No References"
                         print(f"  No valid references found. Assigning reference_set ID {ref_set_id}.")
                    elif frozen_ref_keys not in reference_set_cache:
                        cursor.execute("INSERT INTO reference_set DEFAULT VALUES")
                        ref_set_id = cursor.lastrowid
                        reference_set_cache[frozen_ref_keys] = ref_set_id
                        print(f"  Creating new reference_set ID: {ref_set_id} for {frozen_ref_keys}")
                        for key in frozen_ref_keys:
                            cursor.execute("INSERT INTO reference_set_membership (reference_set_id, bibtex_key) VALUES (?, ?)", (ref_set_id, key))
                    else:
                        ref_set_id = reference_set_cache[frozen_ref_keys]
                        print(f"  Found existing reference_set ID: {ref_set_id}")


                    # --- 5. Insert Thermal Analysis Entry ---
                    thermal_description = row.get('thermal_description', '').strip()
                    print(f"  Creating thermal_analysis_entry linking Obj:{object_id}, SWSet:{sw_set_id}, RefSet:{ref_set_id}")
                    cursor.execute(
                        """
                        INSERT INTO thermal_analysis_entry
                        (object_id, software_set_id, reference_set_id, thermal_description)
                        VALUES (?, ?, ?, ?)
                        """,
                        (object_id, sw_set_id, ref_set_id, thermal_description)
                    )

                except Exception as e:
                    print(f"!!!!!!!! Error processing row {row_num}: {e} !!!!!!!!")
                    skipped_rows += 1
                    # Decide whether to continue or stop
                    continue # Skip to next row on error
                    # raise # Stop execution on error

        conn.commit()
        print(f"\nSuccessfully processed {entry_count - skipped_rows} data rows ({skipped_rows} skipped due to errors).")

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_CSV_FILE}' not found.")
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Database error during processing: {e}")
        if conn: # Make sure conn exists before trying to rollback
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    # 1. Initialize DB (Create tables)
    if init_db(): # Only proceed if initialization succeeds
        # 2. Populate Reference table from BibTeX file
        valid_keys = populate_references_from_bibtex(BIBTEX_FILE)

        # 3. Process main CSV data using the keys from BibTeX
        process_data(valid_keys)