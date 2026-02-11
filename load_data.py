import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "cell-count.csv"
DB_FILE = BASE_DIR / "cell_counts.db"

def print_sample_rows(db_file=DB_FILE, limit=10):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    tables = {
        "projects": "SELECT project_id FROM projects ORDER BY project_id LIMIT ?",
        "subjects": "SELECT subject_id, condition, age, sex, treatment, response, project_id FROM subjects ORDER BY subject_id LIMIT ?",
        "cell_counts": """
            SELECT sample_id, sample_type, time_from_treatment_start,
                b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte, subject_id
            FROM cell_counts ORDER BY sample_id LIMIT ?
        """
    }

    for table_name, query in tables.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        print(f"\nTotal rows in {table_name}: {total}")
        print(f"=== {table_name.upper()} (first {limit} rows) ===")
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    conn.close()


def create_schema(conn):
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS cell_counts;
    DROP TABLE IF EXISTS subjects;
    DROP TABLE IF EXISTS projects;

    CREATE TABLE projects (
        project_id TEXT PRIMARY KEY
    );

    CREATE TABLE subjects (
        subject_id TEXT PRIMARY KEY,
        condition TEXT NOT NULL,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL CHECK (sex IN ('M', 'F')),
        treatment TEXT NOT NULL,
        response TEXT CHECK (response IN ('yes', 'no')) DEFAULT NULL,
        project_id TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );

    CREATE TABLE cell_counts (
        sample_id TEXT PRIMARY KEY,
        sample_type TEXT NOT NULL,
        time_from_treatment_start INTEGER NOT NULL,
        b_cell INTEGER NOT NULL,
        cd8_t_cell INTEGER NOT NULL,
        cd4_t_cell INTEGER NOT NULL,
        nk_cell INTEGER NOT NULL,
        monocyte INTEGER NOT NULL,
        subject_id TEXT NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    );
    """)
    conn.commit()

def load_csv(conn):
    cursor = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Insert project
            cursor.execute("""
                INSERT OR IGNORE INTO projects (project_id) VALUES (?)
            """, (row["project"],))

            # Normalize response
            response = row["response"].strip() or None

            try:
                # Check if subject exists
                cursor.execute("""
                    SELECT subject_id, condition, age, sex, treatment, response, project_id
                    FROM subjects WHERE subject_id = ?
                """, (row["subject"],))
                existing = cursor.fetchone()

                if existing:
                    # Compare existing data with new data
                    existing_data = tuple(existing)
                    new_data = (
                        row["subject"], row["condition"], int(row["age"]), row["sex"], row["treatment"], response, row["project"], 
                    )
                    if existing_data != new_data:
                        # Data differs -> raise exception
                        raise Exception(f"Data Integrity Check Failed: \nData Row #1: {existing}.\nData Row #2: {new_data}")
                else:
                    # Subject does not exist -> insert
                    cursor.execute("""
                        INSERT INTO subjects (
                            subject_id, condition, age, sex, treatment, response, project_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row["subject"], row["condition"], int(row["age"]), row["sex"], row["treatment"], response, row["project"],
                    ))
            except sqlite3.IntegrityError as e:
                print(f"Failed to insert sample {row['sample']}: {e} | Row data: {row}")

            # Insert cell counts
            try:
                cursor.execute("""
                    INSERT INTO cell_counts (
                        sample_id, sample_type, time_from_treatment_start,
                        b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte, subject_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["sample"], row["sample_type"],
                    int(row["time_from_treatment_start"]),
                    int(row["b_cell"]), int(row["cd8_t_cell"]),
                    int(row["cd4_t_cell"]), int(row["nk_cell"]), 
                    int(row["monocyte"]), row["subject"], 
                ))
            except sqlite3.IntegrityError as e:
                print(f"Failed to insert cell_counts for sample {row['sample']}: {e} | Row data: {row}")

    conn.commit()

def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"Could not find {CSV_FILE}")

    conn = sqlite3.connect(DB_FILE)
    create_schema(conn)
    load_csv(conn)
    conn.close()

    print(f"Database created successfully: {DB_FILE}")
    print_sample_rows(limit=10)
    input("Press Enter to End task...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{type(e)}: {e}")
        input("Press Enter to End task...")

