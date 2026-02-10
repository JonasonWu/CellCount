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
        "subjects": "SELECT subject_id, age, sex FROM subjects ORDER BY subject_id LIMIT ?",
        "samples": """
            SELECT sample_id, subject_id, project_id, condition, treatment, response,
                sample_type, time_from_treatment_start
            FROM samples ORDER BY sample_id LIMIT ?
        """,
        "cell_counts": """
            SELECT sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
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
    DROP TABLE IF EXISTS samples;
    DROP TABLE IF EXISTS subjects;
    DROP TABLE IF EXISTS projects;

    CREATE TABLE projects (
        project_id TEXT PRIMARY KEY
    );

    CREATE TABLE subjects (
        subject_id TEXT PRIMARY KEY,
        age INTEGER NOT NULL,
        sex TEXT NOT NULL CHECK (sex IN ('M', 'F'))
    );

    CREATE TABLE samples (
        sample_id TEXT PRIMARY KEY,
        subject_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        condition TEXT NOT NULL,
        treatment TEXT NOT NULL,
        response TEXT CHECK (response IN ('yes', 'no')) DEFAULT NULL,
        sample_type TEXT NOT NULL,
        time_from_treatment_start INTEGER NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (project_id) REFERENCES projects(project_id)
    );

    CREATE TABLE cell_counts (
        sample_id TEXT PRIMARY KEY,
        b_cell INTEGER NOT NULL,
        cd8_t_cell INTEGER NOT NULL,
        cd4_t_cell INTEGER NOT NULL,
        nk_cell INTEGER NOT NULL,
        monocyte INTEGER NOT NULL,
        FOREIGN KEY (sample_id) REFERENCES samples(sample_id)
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

            cursor.execute("""
                INSERT OR IGNORE INTO subjects (subject_id, age, sex) VALUES (?, ?, ?)
            """, (row["subject"], int(row["age"]), row["sex"]))

            # Normalize response
            response = row["response"].strip() or None

            # Insert sample
            try:
                cursor.execute("""
                    INSERT INTO samples (
                        sample_id, subject_id, project_id, condition, treatment,
                        response, sample_type, time_from_treatment_start
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["sample"], row["subject"], row["project"], row["condition"],
                    row["treatment"], response, row["sample_type"],
                    int(row["time_from_treatment_start"])
                ))
            except sqlite3.IntegrityError as e:
                print(f"Failed to insert sample {row['sample']}: {e} | Row data: {row}")

            # Insert cell counts
            try:
                cursor.execute("""
                    INSERT INTO cell_counts (
                        sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row["sample"], int(row["b_cell"]), int(row["cd8_t_cell"]),
                    int(row["cd4_t_cell"]), int(row["nk_cell"]), int(row["monocyte"])
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

