import sqlite3 as sql

conn = sql.connect("Numberplates1.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS temp_numberplate1 (
                    car_id INTEGER PRIMARY KEY,
                    license_plate TEXT,
                    confidence_score REAL,
                    finalized CHAR(1) NOT NULL,
                    iter INTEGER,
                    time REAL
)''')

# Global dictionary to track start times for each car_id
start_times = {}

def add_to_database(numberplate, score, car_id, current_time):
    if car_id not in start_times:
        start_times[car_id] = current_time

    elapsed_time = current_time - start_times[car_id]

    cursor.execute("SELECT * FROM temp_numberplate1 WHERE car_id = ?", (car_id,))
    new_info = cursor.fetchone()

    if new_info is None:
        cursor.execute("INSERT INTO temp_numberplate1 (license_plate, confidence_score, car_id, finalized, iter, time) VALUES (?, ?, ?, ?, ?, ?)", 
                       (numberplate, score, car_id, finalize(score), 0, elapsed_time))
        conn.commit()
    else:
        if elapsed_time < 1000:
            if new_info[3] == 'N':
                if new_info[4] >= 7 or new_info[2] > 0.7:
                    cursor.execute("UPDATE temp_numberplate1 SET finalized = ? WHERE car_id = ?", ('Y', car_id))
                    conn.commit()
                elif new_info[4] < 7:
                    if new_info[1] == numberplate:
                        cursor.execute("UPDATE temp_numberplate1 SET confidence_score = ?, iter = ?, time = ? WHERE car_id = ?", 
                                       (max(score, new_info[2]), new_info[4] + 1, elapsed_time, car_id))
                    elif score > new_info[2]:
                        cursor.execute("UPDATE temp_numberplate1 SET license_plate = ?, confidence_score = ?, iter = ?, time = ? WHERE car_id = ?", 
                                       (numberplate, score, 1, elapsed_time, car_id))
                    conn.commit()
        elif elapsed_time > 1000:
            manual_plate_text = input("Detection taking too long. Enter the vehicle number: ").upper()
            cursor.execute("UPDATE temp_numberplate1 SET license_plate = ?, confidence_score = ?, iter = ?, time = ?, finalized = ? WHERE car_id = ?", 
                           (manual_plate_text, 1.0, 1, elapsed_time, 'Y', car_id))
            conn.commit()

def get_conformation(car_id):
    cursor.execute("SELECT * FROM temp_numberplate1 WHERE car_id = ?", (car_id,))
    info = cursor.fetchone()
    if info is None:
        return False
    return info[3] == 'Y'

def finalize(score):
    if score > 0.7:
        return 'Y'
    return 'N'

# Debugging printout (uncomment to see table structure and contents)
# print(cursor.execute("PRAGMA table_info(temp_numberplate1);").fetchall())
# print(cursor.execute("SELECT * FROM temp_numberplate1;").fetchall())
# cursor.execute("DROP TABLE temp_numberplate1;")
# conn.commit()


# print(cursor.execute("PRAGMA table_info(temp_numberplate1);").fetchall())
print(cursor.execute("SELECT * FROM temp_numberplate1;").fetchall())
# cursor.execute("Drop table temp_numberplate1;")
# conn.commit()
