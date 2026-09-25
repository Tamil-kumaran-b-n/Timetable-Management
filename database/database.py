import os
import sqlite3
import hashlib
import hmac
import secrets


# =========================================================
# DATABASE PATH
# =========================================================

DB_NAME = os.path.join(
    os.path.dirname(__file__),
    "timetable.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    conn = sqlite3.connect(DB_NAME, timeout=15)

    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = 10000")
    conn.execute("PRAGMA temp_store = MEMORY")

    return conn


# =========================================================
# SECURITY / PASSWORD HASHING (PBKDF2-HMAC-SHA256 WITH SALT)
# =========================================================

def hash_password(password: str) -> str:
    """Hash a password using a secure random salt and PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return f"{salt}${key}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a plain password against a salted PBKDF2 hash."""
    try:
        if not stored_hash or "$" not in stored_hash:
            return False
        salt, key = stored_hash.split("$", 1)
        test_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()
        return hmac.compare_digest(key, test_key)
    except Exception:
        return False



# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():

    conn = get_connection()

    try:

        # =================================================
        # USERS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )

        # =================================================
        # FACULTY
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS faculty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                faculty_id TEXT UNIQUE,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT,
                phone TEXT
            )
            """
        )

        # =================================================
        # SUBJECTS
        #
        # hours_per_week is retained for compatibility
        # with the existing database.
        #
        # Actual workload periods are stored in
        # faculty_workload.
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT UNIQUE NOT NULL,
                subject_name TEXT NOT NULL,
                department TEXT NOT NULL,
                semester TEXT NOT NULL,
                hours_per_week INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        # =================================================
        # CLASSROOMS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT UNIQUE NOT NULL,
                room_name TEXT NOT NULL,
                building TEXT NOT NULL,
                room_type TEXT NOT NULL,
                capacity INTEGER NOT NULL
            )
            """
        )

        # =================================================
        # CLASSES
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                department TEXT NOT NULL,
                semester TEXT NOT NULL,
                academic_year TEXT NOT NULL,

                UNIQUE(
                    class_name,
                    department,
                    semester,
                    academic_year
                )
            )
            """
        )

        # =================================================
        # SUBJECT → FACULTY
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS subject_faculty (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                subject_id INTEGER UNIQUE NOT NULL,

                faculty_id INTEGER NOT NULL,

                FOREIGN KEY(subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(faculty_id)
                    REFERENCES faculty(id)
                    ON DELETE CASCADE
            )
            """
        )

        # =================================================
        # CLASS → SUBJECT
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS class_subject (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                class_id INTEGER NOT NULL,

                subject_id INTEGER NOT NULL,

                FOREIGN KEY(class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE,

                FOREIGN KEY(subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE,

                UNIQUE(
                    class_id,
                    subject_id
                )
            )
            """
        )

        # =================================================
        # APP SETTINGS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        # =================================================
        # DEFAULT SEEDING: INITIAL ADMINISTRATOR
        # =================================================
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", hash_password("admin123"), "Administrator")
            )

        
        # Performance Indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timetable_class ON timetable(class_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timetable_faculty ON timetable(faculty_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timetable_day_period ON timetable(day_order, period)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_faculty_dept ON faculty(department)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subjects_dept_sem ON subjects(department, semester)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_classes_dept_sem ON classes(department, semester)")

        conn.commit()

    finally:

        conn.close()

    print("Database created successfully.")


# =========================================================
# USER & AUTHENTICATION FUNCTIONS
# =========================================================

def add_user(
    username: str,
    password: str,
    role: str = "Faculty",
    full_name: str = None,
    department: str = "General",
    email: str = "",
    phone: str = ""
):
    """Register a new user with salted PBKDF2 password encryption.
    New registered accounts default to Faculty and are automatically added to the faculty list.
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?)",
            (username,)
        )
        if cursor.fetchone():
            return False, f"Username '{username}' already exists. Please choose a different name."

        encrypted_pwd = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, encrypted_pwd, role)
        )

        # If faculty user, automatically register in the faculty table for timetable and workload assignments
        if role == "Faculty":
            display_name = full_name.strip() if full_name and full_name.strip() else username
            fac_code = f"FAC-{username.upper()}"
            dept = department.strip() if department and department.strip() else "General"
            mail = email.strip() if email else f"{username.lower()}@college.edu"

            cursor.execute(
                "SELECT id FROM faculty WHERE LOWER(name) = LOWER(?) OR LOWER(faculty_id) = LOWER(?)",
                (display_name, fac_code)
            )
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO faculty (faculty_id, name, department, email, phone)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (fac_code, display_name, dept, mail, phone)
                )

        conn.commit()
        return True, "Account created successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"
    finally:
        conn.close()


def get_faculty_for_user(username: str):
    """Fetch the faculty database record matching a username or name."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, faculty_id, name, department, email, phone
            FROM faculty
            WHERE LOWER(name) = LOWER(?)
               OR LOWER(faculty_id) = LOWER(?)
               OR LOWER(faculty_id) = LOWER(?)
               OR LOWER(name) LIKE LOWER(?)
            LIMIT 1
            """,
            (username.strip(), username.strip(), f"FAC-{username.strip().upper()}", f"%{username.strip()}%")
        )
        return cursor.fetchone()
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    """Authenticate a user using secure salted PBKDF2 hash verification."""
    username = username.strip()
    if not username or not password:
        return None

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, role FROM users WHERE LOWER(username) = LOWER(?)",
            (username,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        user_id, user_name, stored_hash, role = row
        if verify_password(password, stored_hash):
            user_dict = {
                "id": user_id,
                "username": user_name,
                "role": role
            }
            if role == "Faculty":
                cursor.execute(
                    """
                    SELECT id, faculty_id, name, department
                    FROM faculty
                    WHERE LOWER(name) = LOWER(?)
                       OR LOWER(faculty_id) = LOWER(?)
                       OR LOWER(faculty_id) = LOWER(?)
                       OR LOWER(name) LIKE LOWER(?)
                    LIMIT 1
                    """,
                    (user_name, user_name, f"FAC-{user_name.upper()}", f"%{user_name}%")
                )
                fac_row = cursor.fetchone()
                if fac_row:
                    user_dict["faculty_id"] = fac_row[0]
                    user_dict["faculty_code"] = fac_row[1]
                    user_dict["full_name"] = fac_row[2]
                    user_dict["department"] = fac_row[3]
            return user_dict
        return None
    finally:
        conn.close()


def get_user_by_username(username: str):
    """Fetch user basic details by username."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, role FROM users WHERE LOWER(username) = LOWER(?)",
            (username.strip(),)
        )
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "username": row[1], "role": row[2]}
        return None
    finally:
        conn.close()


# =========================================================
# APP SETTINGS FUNCTIONS
# =========================================================

def get_app_setting(key: str, default=None):
    """Retrieve an application setting value from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM app_settings WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        return row[0] if row else default
    except Exception:
        return default
    finally:
        conn.close()


def set_app_setting(key: str, value: str):
    """Save or update an application setting in the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
            (key, str(value))
        )
        conn.commit()
    finally:
        conn.close()


# =========================================================
# FACULTY FUNCTIONS
# =========================================================

def add_faculty(
    faculty_id,
    name,
    department,
    email="",
    phone=""
):

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO faculty
            (
                faculty_id,
                name,
                department,
                email,
                phone
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                faculty_id,
                name,
                department,
                email,
                phone
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_all_faculty():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                faculty_id,
                name,
                department,
                email,
                phone

            FROM faculty

            ORDER BY name
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def update_faculty(
    record_id,
    faculty_id,
    name,
    department,
    email,
    phone
):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE faculty

            SET
                faculty_id = ?,
                name = ?,
                department = ?,
                email = ?,
                phone = ?

            WHERE id = ?
            """,
            (
                faculty_id,
                name,
                department,
                email,
                phone,
                record_id
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def delete_faculty(record_id):

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM faculty
            WHERE id = ?
            """,
            (record_id,)
        )

        conn.commit()

    finally:

        conn.close()


def search_faculty(search_text):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                faculty_id,
                name,
                department,
                email,
                phone

            FROM faculty

            WHERE
                faculty_id LIKE ?
                OR name LIKE ?
                OR department LIKE ?
                OR email LIKE ?
                OR phone LIKE ?

            ORDER BY name
            """,
            (
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%"
            )
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# SUBJECT FUNCTIONS
# =========================================================

def add_subject(
    subject_code,
    subject_name,
    department,
    semester
):

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO subjects
            (
                subject_code,
                subject_name,
                department,
                semester,
                hours_per_week
            )
            VALUES (?, ?, ?, ?, 0)
            """,
            (
                subject_code,
                subject_name,
                department,
                semester
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_all_subjects():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                subject_code,
                subject_name,
                department,
                semester

            FROM subjects

            ORDER BY subject_code
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def update_subject(
    record_id,
    subject_code,
    subject_name,
    department,
    semester
):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE subjects

            SET
                subject_code = ?,
                subject_name = ?,
                department = ?,
                semester = ?

            WHERE id = ?
            """,
            (
                subject_code,
                subject_name,
                department,
                semester,
                record_id
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def delete_subject(record_id):

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM subjects
            WHERE id = ?
            """,
            (record_id,)
        )

        conn.commit()

    finally:

        conn.close()


def search_subjects(search_text):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                subject_code,
                subject_name,
                department,
                semester

            FROM subjects

            WHERE
                subject_code LIKE ?
                OR subject_name LIKE ?
                OR department LIKE ?
                OR semester LIKE ?

            ORDER BY subject_code
            """,
            (
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%"
            )
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# CLASSROOM FUNCTIONS
# =========================================================

def add_classroom(
    room_number,
    room_name,
    building,
    room_type,
    capacity
):

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO classrooms
            (
                room_number,
                room_name,
                building,
                room_type,
                capacity
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                room_number,
                room_name,
                building,
                room_type,
                capacity
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_all_classrooms():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                room_number,
                room_name,
                building,
                room_type,
                capacity

            FROM classrooms

            ORDER BY room_number
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def update_classroom(
    record_id,
    room_number,
    room_name,
    building,
    room_type,
    capacity
):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE classrooms

            SET
                room_number = ?,
                room_name = ?,
                building = ?,
                room_type = ?,
                capacity = ?

            WHERE id = ?
            """,
            (
                room_number,
                room_name,
                building,
                room_type,
                capacity,
                record_id
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def delete_classroom(record_id):

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM classrooms
            WHERE id = ?
            """,
            (record_id,)
        )

        conn.commit()

    finally:

        conn.close()


def search_classrooms(search_text):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                room_number,
                room_name,
                building,
                room_type,
                capacity

            FROM classrooms

            WHERE
                room_number LIKE ?
                OR room_name LIKE ?
                OR building LIKE ?
                OR room_type LIKE ?

            ORDER BY room_number
            """,
            (
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%"
            )
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# CLASS FUNCTIONS
# =========================================================

def add_class(
    class_name,
    department,
    semester,
    academic_year
):

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO classes
            (
                class_name,
                department,
                semester,
                academic_year
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                class_name,
                department,
                semester,
                academic_year
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_all_classes():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                class_name,
                department,
                semester,
                academic_year

            FROM classes

            ORDER BY
                department,
                semester,
                class_name
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def update_class(
    record_id,
    class_name,
    department,
    semester,
    academic_year
):

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE classes

            SET
                class_name = ?,
                department = ?,
                semester = ?,
                academic_year = ?

            WHERE id = ?
            """,
            (
                class_name,
                department,
                semester,
                academic_year,
                record_id
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def delete_class(record_id):

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM classes
            WHERE id = ?
            """,
            (record_id,)
        )

        conn.commit()

    finally:

        conn.close()


def search_classes(search_text):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                class_name,
                department,
                semester,
                academic_year

            FROM classes

            WHERE
                class_name LIKE ?
                OR department LIKE ?
                OR semester LIKE ?
                OR academic_year LIKE ?

            ORDER BY
                department,
                semester,
                class_name
            """,
            (
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%",
                f"%{search_text}%"
            )
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# SUBJECT → FACULTY ASSIGNMENT
# =========================================================

def assign_faculty_to_subject(
    subject_id,
    faculty_id
):

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO subject_faculty
            (
                subject_id,
                faculty_id
            )
            VALUES (?, ?)
            """,
            (
                subject_id,
                faculty_id
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_all_subject_faculty():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                sf.id,
                sf.subject_id,
                sf.faculty_id,
                s.subject_code,
                s.subject_name,
                f.faculty_id,
                f.name,
                s.department,
                s.semester

            FROM subject_faculty sf

            INNER JOIN subjects s
                ON sf.subject_id = s.id

            INNER JOIN faculty f
                ON sf.faculty_id = f.id

            ORDER BY
                s.subject_code
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def get_unassigned_subjects():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                s.id,
                s.subject_code,
                s.subject_name,
                s.department,
                s.semester

            FROM subjects s

            LEFT JOIN subject_faculty sf
                ON s.id = sf.subject_id

            WHERE sf.subject_id IS NULL

            ORDER BY
                s.subject_code
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def get_all_faculty_for_assignment():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                id,
                faculty_id,
                name,
                department

            FROM faculty

            ORDER BY name
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def delete_subject_faculty(
    assignment_id
):

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM subject_faculty
            WHERE id = ?
            """,
            (assignment_id,)
        )

        conn.commit()

    finally:

        conn.close()


def get_subject_faculty_by_subject(
    subject_id
):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                sf.id,
                sf.subject_id,
                sf.faculty_id,
                s.subject_code,
                s.subject_name,
                f.faculty_id,
                f.name,
                s.department,
                s.semester

            FROM subject_faculty sf

            INNER JOIN subjects s
                ON sf.subject_id = s.id

            INNER JOIN faculty f
                ON sf.faculty_id = f.id

            WHERE sf.subject_id = ?
            """,
            (subject_id,)
        )

        return cursor.fetchone()

    finally:

        conn.close()


# =========================================================
# CLASS → SUBJECT ASSIGNMENT
# =========================================================

def assign_subject_to_class(
    class_id,
    subject_id
):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT id
            FROM subject_faculty
            WHERE subject_id = ?
            """,
            (subject_id,)
        )

        faculty_assignment = cursor.fetchone()

        if faculty_assignment is None:

            return "NO_FACULTY"

        conn.execute(
            """
            INSERT INTO class_subject
            (
                class_id,
                subject_id
            )
            VALUES (?, ?)
            """,
            (
                class_id,
                subject_id
            )
        )

        conn.commit()

        return "SUCCESS"

    except sqlite3.IntegrityError:

        return "DUPLICATE"

    finally:

        conn.close()


def get_all_class_subjects():

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                cs.id,

                c.id,
                c.class_name,
                c.department,
                c.semester,
                c.academic_year,

                s.id,
                s.subject_code,
                s.subject_name,

                f.id,
                f.name

            FROM class_subject cs

            INNER JOIN classes c
                ON cs.class_id = c.id

            INNER JOIN subjects s
                ON cs.subject_id = s.id

            LEFT JOIN subject_faculty sf
                ON s.id = sf.subject_id

            LEFT JOIN faculty f
                ON sf.faculty_id = f.id

            ORDER BY
                c.class_name,
                s.subject_code
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def get_subjects_for_class_assignment(
    class_id
):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                department,
                semester

            FROM classes

            WHERE id = ?
            """,
            (class_id,)
        )

        class_record = cursor.fetchone()

        if class_record is None:

            return []

        department = class_record[0]
        semester = class_record[1]

        cursor = conn.execute(
            """
            SELECT
                s.id,
                s.subject_code,
                s.subject_name,
                s.department,
                s.semester,
                f.id,
                f.name

            FROM subjects s

            INNER JOIN subject_faculty sf
                ON s.id = sf.subject_id

            INNER JOIN faculty f
                ON sf.faculty_id = f.id

            WHERE
                LOWER(TRIM(s.department))
                    = LOWER(TRIM(?))

                AND LOWER(TRIM(s.semester))
                    = LOWER(TRIM(?))

                AND s.id NOT IN
                (
                    SELECT subject_id
                    FROM class_subject
                    WHERE class_id = ?
                )

            ORDER BY
                s.subject_code
            """,
            (
                department,
                semester,
                class_id
            )
        )

        return cursor.fetchall()

    finally:

        conn.close()


def get_class_subjects_by_class(
    class_id
):

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                cs.id,

                c.id,
                c.class_name,
                c.department,
                c.semester,
                c.academic_year,

                s.id,
                s.subject_code,
                s.subject_name,

                f.id,
                f.name

            FROM class_subject cs

            INNER JOIN classes c
                ON cs.class_id = c.id

            INNER JOIN subjects s
                ON cs.subject_id = s.id

            LEFT JOIN subject_faculty sf
                ON s.id = sf.subject_id

            LEFT JOIN faculty f
                ON sf.faculty_id = f.id

            WHERE c.id = ?

            ORDER BY
                s.subject_code
            """,
            (class_id,)
        )

        return cursor.fetchall()

    finally:

        conn.close()


def delete_class_subject(
    assignment_id
):

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM class_subject
            WHERE id = ?
            """,
            (assignment_id,)
        )

        conn.commit()

    finally:

        conn.close()


# =========================================================
# DATABASE TEST
# =========================================================

if __name__ == "__main__":

    create_tables()