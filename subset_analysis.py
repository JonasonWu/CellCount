import sqlite3
from typing import Literal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "cell_counts.db"

config = {
    "sample_type": "PBMC",
    "condition": "melanoma",
    "treatment": "miraclib",
    "time_from_treatment_start": 0
}

def query_builder(group_by: Literal["project", "response", "sex"]):
    query = "SELECT "
    group_by_query = ""
    if not group_by:
        query += " sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte "
    elif group_by == "project":
        query += " project_id, count(project_id) as sample_count "
        group_by_query = " GROUP BY project_id "
    elif group_by == "response":
        query += " response, count(response) as sample_count"
        group_by_query = " GROUP BY response "
    elif group_by == "sex":
        query += " sex, count(sex) as sample_count"
        group_by_query = " GROUP BY sex "
    else:
        raise Exception("Invalid parameter input for query builder.")
    
    query += """ 
        FROM samples samp 
        JOIN subjects sub on samp.subject_id = sub.subject_id 
        WHERE sample_type = ? and condition = ? and treatment = ? and time_from_treatment_start = ?
        """
    query += group_by_query
    return query, (config["sample_type"], config["condition"], config["treatment"], config["time_from_treatment_start"])

def print_results(cursor):
    """Fetches the results of the cursor, then prints them out. Assumes that there is very few results from that query. """
    headers = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    for result in results:
        print(f"For {headers[0]} of {result[0]}, the {headers[1]} is {result[1]}.")
    

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Analyzing all melanoma PBMC samples at baseline from patients who have been treated with miraclib.")

    query, parameters = query_builder(group_by="project")
    cursor.execute(query, parameters)
    print_results(cursor)
    query, parameters = query_builder(group_by="response")
    cursor.execute(query, parameters)
    print_results(cursor)
    query, parameters = query_builder(group_by="sex")
    cursor.execute(query, parameters)
    print_results(cursor)
    conn.close()
    input("Press Enter to complete...")

if __name__ == "__main__":
    main()
