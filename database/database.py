import sys
import os
import sqlite3
import hashlib
import hmac
import secrets
app_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'SmartTimetable')
os.makedirs(app_dir, exist_ok=True)
DB_NAME = os.path.join(app_dir, 'timetable.db')

def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=15)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    conn.execute('PRAGMA synchronous = NORMAL')
    conn.execute('PRAGMA cache_size = 10000')
    conn.execute('PRAGMA temp_store = MEMORY')
    return conn

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f'{salt}${key}'

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        if not stored_hash or '$' not in stored_hash:
            return False
        salt, key = stored_hash.split('$', 1)
        test_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return hmac.compare_digest(key, test_key)
    except Exception:
        return False

def create_tables():
    conn = get_connection()
    try:
        conn.execute('\n            CREATE TABLE IF NOT EXISTS users (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                username TEXT UNIQUE NOT NULL,\n                password TEXT NOT NULL,\n                role TEXT NOT NULL\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS faculty (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                faculty_id TEXT UNIQUE,\n                name TEXT NOT NULL,\n                department TEXT NOT NULL,\n                email TEXT,\n                phone TEXT\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS subjects (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                subject_code TEXT UNIQUE NOT NULL,\n                subject_name TEXT NOT NULL,\n                department TEXT NOT NULL,\n                semester TEXT NOT NULL,\n                hours_per_week INTEGER NOT NULL DEFAULT 0\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS classrooms (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                room_number TEXT UNIQUE NOT NULL,\n                room_name TEXT NOT NULL,\n                building TEXT NOT NULL,\n                room_type TEXT NOT NULL,\n                capacity INTEGER NOT NULL\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS classes (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                class_name TEXT NOT NULL,\n                department TEXT NOT NULL,\n                semester TEXT NOT NULL,\n                academic_year TEXT NOT NULL,\n\n                UNIQUE(\n                    class_name,\n                    department,\n                    semester,\n                    academic_year\n                )\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS subject_faculty (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n\n                subject_id INTEGER UNIQUE NOT NULL,\n\n                faculty_id INTEGER NOT NULL,\n\n                FOREIGN KEY(subject_id)\n                    REFERENCES subjects(id)\n                    ON DELETE CASCADE,\n\n                FOREIGN KEY(faculty_id)\n                    REFERENCES faculty(id)\n                    ON DELETE CASCADE\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS class_subject (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n\n                class_id INTEGER NOT NULL,\n\n                subject_id INTEGER NOT NULL,\n\n                FOREIGN KEY(class_id)\n                    REFERENCES classes(id)\n                    ON DELETE CASCADE,\n\n                FOREIGN KEY(subject_id)\n                    REFERENCES subjects(id)\n                    ON DELETE CASCADE,\n\n                UNIQUE(\n                    class_id,\n                    subject_id\n                )\n            )\n            ')
        conn.execute("\n            CREATE TABLE IF NOT EXISTS faculty_workload (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                faculty_id INTEGER NOT NULL,\n                class_id INTEGER NOT NULL,\n                subject_id INTEGER NOT NULL,\n                priority TEXT NOT NULL DEFAULT 'Normal',\n                periods_per_week INTEGER NOT NULL,\n                UNIQUE (faculty_id, class_id, subject_id),\n                FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE,\n                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,\n                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE\n            )\n            ")
        conn.execute('\n            CREATE TABLE IF NOT EXISTS timetable (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                day_order INTEGER NOT NULL,\n                period INTEGER NOT NULL,\n                class_id INTEGER NOT NULL,\n                subject_id INTEGER NOT NULL,\n                faculty_id INTEGER NOT NULL,\n                UNIQUE(day_order, period, class_id),\n                UNIQUE(day_order, period, faculty_id),\n                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,\n                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,\n                FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE\n            )\n            ')
        conn.execute('\n            CREATE TABLE IF NOT EXISTS app_settings (\n                key TEXT PRIMARY KEY,\n                value TEXT NOT NULL\n            )\n            ')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', hash_password('admin123'), 'Administrator'))
        conn.execute('CREATE INDEX IF NOT EXISTS idx_timetable_class ON timetable(class_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_timetable_faculty ON timetable(faculty_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_timetable_day_period ON timetable(day_order, period)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_faculty_dept ON faculty(department)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_subjects_dept_sem ON subjects(department, semester)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_classes_dept_sem ON classes(department, semester)')
        conn.commit()
    finally:
        conn.close()
    print('Database created successfully.')

def add_user(username: str, password: str, role: str='Faculty', full_name: str=None, department: str='General', email: str='', phone: str=''):
    username = username.strip()
    if not username or not password:
        return (False, 'Username and password cannot be empty.')
    if len(username) < 3:
        return (False, 'Username must be at least 3 characters long.')
    if len(password) < 4:
        return (False, 'Password must be at least 4 characters long.')
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE LOWER(username) = LOWER(?)', (username,))
        if cursor.fetchone():
            return (False, f"Username '{username}' already exists. Please choose a different name.")
        encrypted_pwd = hash_password(password)
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, encrypted_pwd, role))
        if role == 'Faculty':
            display_name = full_name.strip() if full_name and full_name.strip() else username
            fac_code = f'FAC-{username.upper()}'
            dept = department.strip() if department and department.strip() else 'General'
            mail = email.strip() if email else f'{username.lower()}@college.edu'
            cursor.execute('SELECT id FROM faculty WHERE LOWER(name) = LOWER(?) OR LOWER(faculty_id) = LOWER(?)', (display_name, fac_code))
            if not cursor.fetchone():
                cursor.execute('\n                    INSERT INTO faculty (faculty_id, name, department, email, phone)\n                    VALUES (?, ?, ?, ?, ?)\n                    ', (fac_code, display_name, dept, mail, phone))
        conn.commit()
        return (True, 'Account created successfully.')
    except Exception as e:
        return (False, f'Database error: {str(e)}')
    finally:
        conn.close()

def get_faculty_for_user(username: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('\n            SELECT id, faculty_id, name, department, email, phone\n            FROM faculty\n            WHERE LOWER(name) = LOWER(?)\n               OR LOWER(faculty_id) = LOWER(?)\n               OR LOWER(faculty_id) = LOWER(?)\n               OR LOWER(name) LIKE LOWER(?)\n            LIMIT 1\n            ', (username.strip(), username.strip(), f'FAC-{username.strip().upper()}', f'%{username.strip()}%'))
        return cursor.fetchone()
    finally:
        conn.close()

def authenticate_user(username: str, password: str):
    username = username.strip()
    if not username or not password:
        return None
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password, role FROM users WHERE LOWER(username) = LOWER(?)', (username,))
        row = cursor.fetchone()
        if not row:
            return None
        user_id, user_name, stored_hash, role = row
        if verify_password(password, stored_hash):
            user_dict = {'id': user_id, 'username': user_name, 'role': role}
            if role == 'Faculty':
                cursor.execute('\n                    SELECT id, faculty_id, name, department\n                    FROM faculty\n                    WHERE LOWER(name) = LOWER(?)\n                       OR LOWER(faculty_id) = LOWER(?)\n                       OR LOWER(faculty_id) = LOWER(?)\n                       OR LOWER(name) LIKE LOWER(?)\n                    LIMIT 1\n                    ', (user_name, user_name, f'FAC-{user_name.upper()}', f'%{user_name}%'))
                fac_row = cursor.fetchone()
                if fac_row:
                    user_dict['faculty_id'] = fac_row[0]
                    user_dict['faculty_code'] = fac_row[1]
                    user_dict['full_name'] = fac_row[2]
                    user_dict['department'] = fac_row[3]
            return user_dict
        return None
    finally:
        conn.close()

def get_user_by_username(username: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role FROM users WHERE LOWER(username) = LOWER(?)', (username.strip(),))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'username': row[1], 'role': row[2]}
        return None
    finally:
        conn.close()

def get_app_setting(key: str, default=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        return row[0] if row else default
    except Exception:
        return default
    finally:
        conn.close()

def set_app_setting(key: str, value: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)', (key, str(value)))
        conn.commit()
    finally:
        conn.close()

def add_faculty(faculty_id, name, department, email='', phone=''):
    conn = get_connection()
    try:
        conn.execute('\n            INSERT INTO faculty\n            (\n                faculty_id,\n                name,\n                department,\n                email,\n                phone\n            )\n            VALUES (?, ?, ?, ?, ?)\n            ', (faculty_id, name, department, email, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_faculty():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                faculty_id,\n                name,\n                department,\n                email,\n                phone\n\n            FROM faculty\n\n            ORDER BY name\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def update_faculty(record_id, faculty_id, name, department, email, phone):
    conn = get_connection()
    try:
        conn.execute('\n            UPDATE faculty\n\n            SET\n                faculty_id = ?,\n                name = ?,\n                department = ?,\n                email = ?,\n                phone = ?\n\n            WHERE id = ?\n            ', (faculty_id, name, department, email, phone, record_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_faculty(record_id):
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM faculty\n            WHERE id = ?\n            ', (record_id,))
        conn.commit()
    finally:
        conn.close()

def search_faculty(search_text):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                faculty_id,\n                name,\n                department,\n                email,\n                phone\n\n            FROM faculty\n\n            WHERE\n                faculty_id LIKE ?\n                OR name LIKE ?\n                OR department LIKE ?\n                OR email LIKE ?\n                OR phone LIKE ?\n\n            ORDER BY name\n            ', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        return cursor.fetchall()
    finally:
        conn.close()

def add_subject(subject_code, subject_name, department, semester):
    conn = get_connection()
    try:
        conn.execute('\n            INSERT INTO subjects\n            (\n                subject_code,\n                subject_name,\n                department,\n                semester,\n                hours_per_week\n            )\n            VALUES (?, ?, ?, ?, 0)\n            ', (subject_code, subject_name, department, semester))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_subjects():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                subject_code,\n                subject_name,\n                department,\n                semester\n\n            FROM subjects\n\n            ORDER BY subject_code\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def update_subject(record_id, subject_code, subject_name, department, semester):
    conn = get_connection()
    try:
        conn.execute('\n            UPDATE subjects\n\n            SET\n                subject_code = ?,\n                subject_name = ?,\n                department = ?,\n                semester = ?\n\n            WHERE id = ?\n            ', (subject_code, subject_name, department, semester, record_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_subject(record_id):
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM subjects\n            WHERE id = ?\n            ', (record_id,))
        conn.commit()
    finally:
        conn.close()

def search_subjects(search_text):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                subject_code,\n                subject_name,\n                department,\n                semester\n\n            FROM subjects\n\n            WHERE\n                subject_code LIKE ?\n                OR subject_name LIKE ?\n                OR department LIKE ?\n                OR semester LIKE ?\n\n            ORDER BY subject_code\n            ', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        return cursor.fetchall()
    finally:
        conn.close()

def add_classroom(room_number, room_name, building, room_type, capacity):
    conn = get_connection()
    try:
        conn.execute('\n            INSERT INTO classrooms\n            (\n                room_number,\n                room_name,\n                building,\n                room_type,\n                capacity\n            )\n            VALUES (?, ?, ?, ?, ?)\n            ', (room_number, room_name, building, room_type, capacity))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_classrooms():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                room_number,\n                room_name,\n                building,\n                room_type,\n                capacity\n\n            FROM classrooms\n\n            ORDER BY room_number\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def update_classroom(record_id, room_number, room_name, building, room_type, capacity):
    conn = get_connection()
    try:
        conn.execute('\n            UPDATE classrooms\n\n            SET\n                room_number = ?,\n                room_name = ?,\n                building = ?,\n                room_type = ?,\n                capacity = ?\n\n            WHERE id = ?\n            ', (room_number, room_name, building, room_type, capacity, record_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_classroom(record_id):
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM classrooms\n            WHERE id = ?\n            ', (record_id,))
        conn.commit()
    finally:
        conn.close()

def search_classrooms(search_text):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                room_number,\n                room_name,\n                building,\n                room_type,\n                capacity\n\n            FROM classrooms\n\n            WHERE\n                room_number LIKE ?\n                OR room_name LIKE ?\n                OR building LIKE ?\n                OR room_type LIKE ?\n\n            ORDER BY room_number\n            ', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        return cursor.fetchall()
    finally:
        conn.close()

def add_class(class_name, department, semester, academic_year):
    conn = get_connection()
    try:
        conn.execute('\n            INSERT INTO classes\n            (\n                class_name,\n                department,\n                semester,\n                academic_year\n            )\n            VALUES (?, ?, ?, ?)\n            ', (class_name, department, semester, academic_year))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_classes():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                class_name,\n                department,\n                semester,\n                academic_year\n\n            FROM classes\n\n            ORDER BY\n                department,\n                semester,\n                class_name\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def update_class(record_id, class_name, department, semester, academic_year):
    conn = get_connection()
    try:
        conn.execute('\n            UPDATE classes\n\n            SET\n                class_name = ?,\n                department = ?,\n                semester = ?,\n                academic_year = ?\n\n            WHERE id = ?\n            ', (class_name, department, semester, academic_year, record_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_class(record_id):
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM classes\n            WHERE id = ?\n            ', (record_id,))
        conn.commit()
    finally:
        conn.close()

def search_classes(search_text):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                class_name,\n                department,\n                semester,\n                academic_year\n\n            FROM classes\n\n            WHERE\n                class_name LIKE ?\n                OR department LIKE ?\n                OR semester LIKE ?\n                OR academic_year LIKE ?\n\n            ORDER BY\n                department,\n                semester,\n                class_name\n            ', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
        return cursor.fetchall()
    finally:
        conn.close()

def assign_faculty_to_subject(subject_id, faculty_id):
    conn = get_connection()
    try:
        conn.execute('\n            INSERT INTO subject_faculty\n            (\n                subject_id,\n                faculty_id\n            )\n            VALUES (?, ?)\n            ', (subject_id, faculty_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_subject_faculty():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                sf.id,\n                sf.subject_id,\n                sf.faculty_id,\n                s.subject_code,\n                s.subject_name,\n                f.faculty_id,\n                f.name,\n                s.department,\n                s.semester\n\n            FROM subject_faculty sf\n\n            INNER JOIN subjects s\n                ON sf.subject_id = s.id\n\n            INNER JOIN faculty f\n                ON sf.faculty_id = f.id\n\n            ORDER BY\n                s.subject_code\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def get_unassigned_subjects():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                s.id,\n                s.subject_code,\n                s.subject_name,\n                s.department,\n                s.semester\n\n            FROM subjects s\n\n            LEFT JOIN subject_faculty sf\n                ON s.id = sf.subject_id\n\n            WHERE sf.subject_id IS NULL\n\n            ORDER BY\n                s.subject_code\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def get_all_faculty_for_assignment():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                id,\n                faculty_id,\n                name,\n                department\n\n            FROM faculty\n\n            ORDER BY name\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def delete_subject_faculty(assignment_id):
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM subject_faculty\n            WHERE id = ?\n            ', (assignment_id,))
        conn.commit()
    finally:
        conn.close()

def get_subject_faculty_by_subject(subject_id):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                sf.id,\n                sf.subject_id,\n                sf.faculty_id,\n                s.subject_code,\n                s.subject_name,\n                f.faculty_id,\n                f.name,\n                s.department,\n                s.semester\n\n            FROM subject_faculty sf\n\n            INNER JOIN subjects s\n                ON sf.subject_id = s.id\n\n            INNER JOIN faculty f\n                ON sf.faculty_id = f.id\n\n            WHERE sf.subject_id = ?\n            ', (subject_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def assign_subject_to_class(class_id, subject_id):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT id\n            FROM subject_faculty\n            WHERE subject_id = ?\n            ', (subject_id,))
        faculty_assignment = cursor.fetchone()
        if faculty_assignment is None:
            return 'NO_FACULTY'
        conn.execute('\n            INSERT INTO class_subject\n            (\n                class_id,\n                subject_id\n            )\n            VALUES (?, ?)\n            ', (class_id, subject_id))
        conn.commit()
        return 'SUCCESS'
    except sqlite3.IntegrityError:
        return 'DUPLICATE'
    finally:
        conn.close()

def get_all_class_subjects():
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                cs.id,\n\n                c.id,\n                c.class_name,\n                c.department,\n                c.semester,\n                c.academic_year,\n\n                s.id,\n                s.subject_code,\n                s.subject_name,\n\n                f.id,\n                f.name\n\n            FROM class_subject cs\n\n            INNER JOIN classes c\n                ON cs.class_id = c.id\n\n            INNER JOIN subjects s\n                ON cs.subject_id = s.id\n\n            LEFT JOIN subject_faculty sf\n                ON s.id = sf.subject_id\n\n            LEFT JOIN faculty f\n                ON sf.faculty_id = f.id\n\n            ORDER BY\n                c.class_name,\n                s.subject_code\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def get_subjects_for_class_assignment(class_id):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                department,\n                semester\n\n            FROM classes\n\n            WHERE id = ?\n            ', (class_id,))
        class_record = cursor.fetchone()
        if class_record is None:
            return []
        department = class_record[0]
        semester = class_record[1]
        cursor = conn.execute('\n            SELECT\n                s.id,\n                s.subject_code,\n                s.subject_name,\n                s.department,\n                s.semester,\n                f.id,\n                f.name\n\n            FROM subjects s\n\n            INNER JOIN subject_faculty sf\n                ON s.id = sf.subject_id\n\n            INNER JOIN faculty f\n                ON sf.faculty_id = f.id\n\n            WHERE\n                LOWER(TRIM(s.department))\n                    = LOWER(TRIM(?))\n\n                AND LOWER(TRIM(s.semester))\n                    = LOWER(TRIM(?))\n\n                AND s.id NOT IN\n                (\n                    SELECT subject_id\n                    FROM class_subject\n                    WHERE class_id = ?\n                )\n\n            ORDER BY\n                s.subject_code\n            ', (department, semester, class_id))
        return cursor.fetchall()
    finally:
        conn.close()

def get_class_subjects_by_class(class_id):
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                cs.id,\n\n                c.id,\n                c.class_name,\n                c.department,\n                c.semester,\n                c.academic_year,\n\n                s.id,\n                s.subject_code,\n                s.subject_name,\n\n                f.id,\n                f.name\n\n            FROM class_subject cs\n\n            INNER JOIN classes c\n                ON cs.class_id = c.id\n\n            INNER JOIN subjects s\n                ON cs.subject_id = s.id\n\n            LEFT JOIN subject_faculty sf\n                ON s.id = sf.subject_id\n\n            LEFT JOIN faculty f\n                ON sf.faculty_id = f.id\n\n            WHERE c.id = ?\n\n            ORDER BY\n                s.subject_code\n            ', (class_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def delete_class_subject(assignment_id):
    conn = get_connection()
    try:
        conn.execute('\n            DELETE FROM class_subject\n            WHERE id = ?\n            ', (assignment_id,))
        conn.commit()
    finally:
        conn.close()
if __name__ == '__main__':
    create_tables()
