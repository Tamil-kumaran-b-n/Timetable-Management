import sqlite3
from database.database import get_connection

def create_workload_table():
    conn = get_connection()
    try:
        conn.execute("\n            CREATE TABLE IF NOT EXISTS faculty_workload\n            (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n\n                faculty_id INTEGER NOT NULL,\n\n                class_id INTEGER NOT NULL,\n\n                subject_id INTEGER NOT NULL,\n\n                priority TEXT NOT NULL\n                    DEFAULT 'Normal',\n\n                periods_per_week INTEGER NOT NULL,\n\n                UNIQUE (\n                    faculty_id,\n                    class_id,\n                    subject_id\n                ),\n\n                FOREIGN KEY (faculty_id)\n                    REFERENCES faculty(id)\n                    ON DELETE CASCADE,\n\n                FOREIGN KEY (class_id)\n                    REFERENCES classes(id)\n                    ON DELETE CASCADE,\n\n                FOREIGN KEY (subject_id)\n                    REFERENCES subjects(id)\n                    ON DELETE CASCADE\n            )\n            ")
        conn.commit()
    finally:
        conn.close()

def add_workload(faculty_id, class_id, subject_id, priority, periods_per_week):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            INSERT INTO faculty_workload\n            (\n                faculty_id,\n                class_id,\n                subject_id,\n                priority,\n                periods_per_week\n            )\n            VALUES (?, ?, ?, ?, ?)\n            ', (faculty_id, class_id, subject_id, priority, periods_per_week))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_workloads():
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n\n                fw.id,\n\n                f.id,\n                f.faculty_id,\n                f.name,\n\n                c.id,\n                c.class_name,\n                c.department,\n                c.semester,\n                c.academic_year,\n\n                s.id,\n                s.subject_code,\n                s.subject_name,\n\n                fw.priority,\n                fw.periods_per_week\n\n            FROM faculty_workload fw\n\n            INNER JOIN faculty f\n                ON fw.faculty_id = f.id\n\n            INNER JOIN classes c\n                ON fw.class_id = c.id\n\n            INNER JOIN subjects s\n                ON fw.subject_id = s.id\n\n            ORDER BY\n                f.name,\n                c.class_name,\n                s.subject_code\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def get_workload_by_id(workload_id):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n\n                fw.id,\n\n                f.id,\n                f.faculty_id,\n                f.name,\n\n                c.id,\n                c.class_name,\n                c.department,\n                c.semester,\n                c.academic_year,\n\n                s.id,\n                s.subject_code,\n                s.subject_name,\n\n                fw.priority,\n                fw.periods_per_week\n\n            FROM faculty_workload fw\n\n            INNER JOIN faculty f\n                ON fw.faculty_id = f.id\n\n            INNER JOIN classes c\n                ON fw.class_id = c.id\n\n            INNER JOIN subjects s\n                ON fw.subject_id = s.id\n\n            WHERE fw.id = ?\n\n            LIMIT 1\n            ', (workload_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_workloads_by_faculty(faculty_id):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n\n                fw.id,\n\n                f.name,\n\n                c.class_name,\n                c.department,\n                c.semester,\n\n                s.subject_code,\n                s.subject_name,\n\n                fw.priority,\n                fw.periods_per_week\n\n            FROM faculty_workload fw\n\n            INNER JOIN faculty f\n                ON fw.faculty_id = f.id\n\n            INNER JOIN classes c\n                ON fw.class_id = c.id\n\n            INNER JOIN subjects s\n                ON fw.subject_id = s.id\n\n            WHERE fw.faculty_id = ?\n\n            ORDER BY\n                c.class_name,\n                s.subject_code\n            ', (faculty_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_workloads_by_class(class_id):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n\n                fw.id,\n\n                c.class_name,\n\n                s.subject_code,\n                s.subject_name,\n\n                f.name,\n\n                fw.priority,\n                fw.periods_per_week\n\n            FROM faculty_workload fw\n\n            INNER JOIN classes c\n                ON fw.class_id = c.id\n\n            INNER JOIN subjects s\n                ON fw.subject_id = s.id\n\n            INNER JOIN faculty f\n                ON fw.faculty_id = f.id\n\n            WHERE fw.class_id = ?\n\n            ORDER BY\n                s.subject_code\n            ', (class_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def update_workload(workload_id, faculty_id, class_id, subject_id, priority, periods_per_week):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            UPDATE faculty_workload\n\n            SET\n                faculty_id = ?,\n                class_id = ?,\n                subject_id = ?,\n                priority = ?,\n                periods_per_week = ?\n\n            WHERE id = ?\n            ', (faculty_id, class_id, subject_id, priority, periods_per_week, workload_id))
        conn.commit()
        if cursor.rowcount == 0:
            return False
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_workload(workload_id):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            DELETE FROM faculty_workload\n\n            WHERE id = ?\n            ', (workload_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return False
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_total_workload_for_faculty(faculty_id):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                COALESCE(\n                    SUM(periods_per_week),\n                    0\n                )\n\n            FROM faculty_workload\n\n            WHERE faculty_id = ?\n            ', (faculty_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return 0
    finally:
        conn.close()

def get_total_workload_for_class(class_id):
    create_workload_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                COALESCE(\n                    SUM(periods_per_week),\n                    0\n                )\n\n            FROM faculty_workload\n\n            WHERE class_id = ?\n            ', (class_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return 0
    finally:
        conn.close()

def workload_exists(faculty_id, class_id, subject_id, exclude_workload_id=None):
    create_workload_table()
    conn = get_connection()
    try:
        if exclude_workload_id is None:
            cursor = conn.execute('\n                SELECT id\n\n                FROM faculty_workload\n\n                WHERE\n                    faculty_id = ?\n                    AND class_id = ?\n                    AND subject_id = ?\n\n                LIMIT 1\n                ', (faculty_id, class_id, subject_id))
        else:
            cursor = conn.execute('\n                SELECT id\n\n                FROM faculty_workload\n\n                WHERE\n                    faculty_id = ?\n                    AND class_id = ?\n                    AND subject_id = ?\n\n                    AND id != ?\n\n                LIMIT 1\n                ', (faculty_id, class_id, subject_id, exclude_workload_id))
        result = cursor.fetchone()
        return result is not None
    finally:
        conn.close()

def clear_all_workloads():
    create_workload_table()
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM faculty_workload\n            ')
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()
create_workload_table()
