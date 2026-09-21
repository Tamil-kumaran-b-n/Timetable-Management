import sqlite3

from database.database import get_connection


# =========================================================
# CREATE WORKLOAD TABLE
# =========================================================

def create_workload_table():

    conn = get_connection()

    try:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS faculty_workload
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                faculty_id INTEGER NOT NULL,

                class_id INTEGER NOT NULL,

                subject_id INTEGER NOT NULL,

                priority TEXT NOT NULL
                    DEFAULT 'Normal',

                periods_per_week INTEGER NOT NULL,

                UNIQUE (
                    faculty_id,
                    class_id,
                    subject_id
                ),

                FOREIGN KEY (faculty_id)
                    REFERENCES faculty(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE
            )
            """
        )

        conn.commit()

    finally:

        conn.close()


# =========================================================
# ADD WORKLOAD
# =========================================================

def add_workload(
    faculty_id,
    class_id,
    subject_id,
    priority,
    periods_per_week
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            INSERT INTO faculty_workload
            (
                faculty_id,
                class_id,
                subject_id,
                priority,
                periods_per_week
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                faculty_id,
                class_id,
                subject_id,
                priority,
                periods_per_week
            )
        )

        conn.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:

        return None

    finally:

        conn.close()


# =========================================================
# GET ALL WORKLOADS
# =========================================================

def get_all_workloads():

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT

                fw.id,

                f.id,
                f.faculty_id,
                f.name,

                c.id,
                c.class_name,
                c.department,
                c.semester,
                c.academic_year,

                s.id,
                s.subject_code,
                s.subject_name,

                fw.priority,
                fw.periods_per_week

            FROM faculty_workload fw

            INNER JOIN faculty f
                ON fw.faculty_id = f.id

            INNER JOIN classes c
                ON fw.class_id = c.id

            INNER JOIN subjects s
                ON fw.subject_id = s.id

            ORDER BY
                f.name,
                c.class_name,
                s.subject_code
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# GET SINGLE WORKLOAD
# =========================================================

def get_workload_by_id(workload_id):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT

                fw.id,

                f.id,
                f.faculty_id,
                f.name,

                c.id,
                c.class_name,
                c.department,
                c.semester,
                c.academic_year,

                s.id,
                s.subject_code,
                s.subject_name,

                fw.priority,
                fw.periods_per_week

            FROM faculty_workload fw

            INNER JOIN faculty f
                ON fw.faculty_id = f.id

            INNER JOIN classes c
                ON fw.class_id = c.id

            INNER JOIN subjects s
                ON fw.subject_id = s.id

            WHERE fw.id = ?

            LIMIT 1
            """,
            (workload_id,)
        )

        return cursor.fetchone()

    finally:

        conn.close()


# =========================================================
# GET WORKLOADS BY FACULTY
# =========================================================

def get_workloads_by_faculty(
    faculty_id
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT

                fw.id,

                f.name,

                c.class_name,
                c.department,
                c.semester,

                s.subject_code,
                s.subject_name,

                fw.priority,
                fw.periods_per_week

            FROM faculty_workload fw

            INNER JOIN faculty f
                ON fw.faculty_id = f.id

            INNER JOIN classes c
                ON fw.class_id = c.id

            INNER JOIN subjects s
                ON fw.subject_id = s.id

            WHERE fw.faculty_id = ?

            ORDER BY
                c.class_name,
                s.subject_code
            """,
            (faculty_id,)
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# GET WORKLOADS BY CLASS
# =========================================================

def get_workloads_by_class(
    class_id
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT

                fw.id,

                c.class_name,

                s.subject_code,
                s.subject_name,

                f.name,

                fw.priority,
                fw.periods_per_week

            FROM faculty_workload fw

            INNER JOIN classes c
                ON fw.class_id = c.id

            INNER JOIN subjects s
                ON fw.subject_id = s.id

            INNER JOIN faculty f
                ON fw.faculty_id = f.id

            WHERE fw.class_id = ?

            ORDER BY
                s.subject_code
            """,
            (class_id,)
        )

        return cursor.fetchall()

    finally:

        conn.close()


# =========================================================
# UPDATE WORKLOAD
# =========================================================

def update_workload(
    workload_id,
    faculty_id,
    class_id,
    subject_id,
    priority,
    periods_per_week
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            UPDATE faculty_workload

            SET
                faculty_id = ?,
                class_id = ?,
                subject_id = ?,
                priority = ?,
                periods_per_week = ?

            WHERE id = ?
            """,
            (
                faculty_id,
                class_id,
                subject_id,
                priority,
                periods_per_week,
                workload_id
            )
        )

        conn.commit()

        # -----------------------------------------
        # Check whether a record was actually found
        # -----------------------------------------

        if cursor.rowcount == 0:

            return False

        return True

    except sqlite3.IntegrityError:

        # Duplicate faculty + class + subject
        return False

    finally:

        conn.close()


# =========================================================
# DELETE WORKLOAD
# =========================================================

def delete_workload(
    workload_id
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            DELETE FROM faculty_workload

            WHERE id = ?
            """,
            (workload_id,)
        )

        conn.commit()

        if cursor.rowcount == 0:

            return False

        return True

    except sqlite3.Error:

        return False

    finally:

        conn.close()


# =========================================================
# TOTAL WORKLOAD FOR FACULTY
# =========================================================

def get_total_workload_for_faculty(
    faculty_id
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                COALESCE(
                    SUM(periods_per_week),
                    0
                )

            FROM faculty_workload

            WHERE faculty_id = ?
            """,
            (faculty_id,)
        )

        result = cursor.fetchone()

        if result:

            return result[0]

        return 0

    finally:

        conn.close()


# =========================================================
# TOTAL WORKLOAD FOR CLASS
# =========================================================

def get_total_workload_for_class(
    class_id
):

    create_workload_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                COALESCE(
                    SUM(periods_per_week),
                    0
                )

            FROM faculty_workload

            WHERE class_id = ?
            """,
            (class_id,)
        )

        result = cursor.fetchone()

        if result:

            return result[0]

        return 0

    finally:

        conn.close()


# =========================================================
# CHECK DUPLICATE WORKLOAD
# =========================================================

def workload_exists(
    faculty_id,
    class_id,
    subject_id,
    exclude_workload_id=None
):

    create_workload_table()

    conn = get_connection()

    try:

        if exclude_workload_id is None:

            cursor = conn.execute(
                """
                SELECT id

                FROM faculty_workload

                WHERE
                    faculty_id = ?
                    AND class_id = ?
                    AND subject_id = ?

                LIMIT 1
                """,
                (
                    faculty_id,
                    class_id,
                    subject_id
                )
            )

        else:

            cursor = conn.execute(
                """
                SELECT id

                FROM faculty_workload

                WHERE
                    faculty_id = ?
                    AND class_id = ?
                    AND subject_id = ?

                    AND id != ?

                LIMIT 1
                """,
                (
                    faculty_id,
                    class_id,
                    subject_id,
                    exclude_workload_id
                )
            )

        result = cursor.fetchone()

        return result is not None

    finally:

        conn.close()


# =========================================================
# CLEAR ALL WORKLOADS
# =========================================================

def clear_all_workloads():

    create_workload_table()

    conn = get_connection()

    try:

        conn.execute(
            """
            DELETE FROM faculty_workload
            """
        )

        conn.commit()

        return True

    except sqlite3.Error:

        return False

    finally:

        conn.close()


# =========================================================
# INITIALIZE TABLE
# =========================================================

create_workload_table()