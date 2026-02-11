import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "cell_counts.db"

def compute_cell_frequencies(db_file=DB_FILE, allow_print=False, save_to_file=""):
    """
    Compute total cell counts and relative percentages for each cell population (one row per sample).
    
    Returns:
        results (list of dicts):
            [
                {
                    'sample': 'sample00000',
                    'total_count': 93214,
                    'b_cell%': 11.7,
                    'cd8_t_cell%': 26.22,
                    'cd4_t_cell%': 21.98,
                    'nk_cell%': 14.87,
                    'monocyte%': 25.21
                },
                ...
            ]
    """

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch all cell counts from the database
    cursor.execute("""
        SELECT sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
        FROM samples
        ORDER BY sample_id
    """)

    results = []

    file_handle = open(BASE_DIR / save_to_file, "w") if save_to_file else None
    header = f"{'sample':<12} {'total_count':<12} {'b_cell%':<10} {'cd8_t_cell%':<12} {'cd4_t_cell%':<12} {'nk_cell%':<10} {'monocyte%':<12}"
    if allow_print:
        print(header)
    if save_to_file:
        file_handle.write(header + "\n")

    for i, row in enumerate(cursor, 1):
        sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte = row

        # Total number of cells
        total_count = b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte

        if total_count == 0:
            b_perc = cd8_perc = cd4_perc = nk_perc = mono_perc = 0.0
        else:
            # Compute percentages
            b_perc = round(b_cell / total_count * 100, 2)
            cd8_perc = round(cd8_t_cell / total_count * 100, 2)
            cd4_perc = round(cd4_t_cell / total_count * 100, 2)
            nk_perc = round(nk_cell / total_count * 100, 2)
            mono_perc = round(monocyte / total_count * 100, 2)

        result_row = {
            "sample": sample_id,
            "total_count": total_count,
            "b_cell_perc": b_perc,
            "cd8_t_cell_perc": cd8_perc,
            "cd4_t_cell_perc": cd4_perc,
            "nk_cell_perc": nk_perc,
            "monocyte_perc": mono_perc
        }

        results.append(result_row)

        result_string = f"{sample_id:<12} {total_count:<12} {b_perc:<10} {cd8_perc:<12} {cd4_perc:<12} {nk_perc:<10} {mono_perc:<12}"
        if save_to_file:
            file_handle.write(result_string + "\n")

        if allow_print:
            print(result_string)
            if not i % 50:
                input("Press Enter to Continue...")
                print(header)

    
    conn.close()
    if file_handle:
        file_handle.close()
    return results

if __name__ == "__main__":
    try:
        allow_print = True if input("Do you want to print relative_frequencies on terminal? (y for yes, anything else means no): ") == "y" else False
        compute_cell_frequencies(allow_print=allow_print, save_to_file="relative_frequencies.txt")
        print("Cell Frequencies computed and written into relative_frequencies.txt file.")
        input("Press Enter to End Task...")
    except Exception as e:
        print(f"{type(e)}: {e}")
        input("Press Enter to End task...")
