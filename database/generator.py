import random
import sqlite3

from database.database import get_connection
from database.workload import create_workload_table


# ============================================================
# TIMETABLE CONFIGURATION
# ============================================================

DAY_ORDERS = 6
PERIODS_PER_DAY = 5

TOTAL_SLOTS_PER_CLASS = DAY_ORDERS * PERIODS_PER_DAY


# ============================================================
# TIMETABLE TABLE
# ============================================================

def create_timetable_table():
    """
    Creates the generated timetable table if it does not exist.

    This table stores the actual generated timetable.
    Faculty workload remains the source of truth.
    """

    conn = get_connection()

    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS timetable
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                day_order INTEGER NOT NULL,
                period INTEGER NOT NULL,

                class_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                faculty_id INTEGER NOT NULL,

                UNIQUE(day_order, period, class_id),
                UNIQUE(day_order, period, faculty_id),

                FOREIGN KEY (class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (faculty_id)
                    REFERENCES faculty(id)
                    ON DELETE CASCADE
            )
            """
        )

        conn.commit()

    finally:
        conn.close()


# ============================================================
# GET WORKLOAD DATA
# ============================================================

def _get_workloads():
    """
    Gets all faculty workloads.

    Workload is the source of truth for timetable generation.
    """

    create_workload_table()

    conn = get_connection()

    try:
        cursor = conn.execute(
            """
            SELECT
                fw.id,
                fw.faculty_id,
                fw.class_id,
                fw.subject_id,
                fw.priority,
                fw.periods_per_week,

                f.name,
                c.class_name,
                s.subject_code,
                s.subject_name

            FROM faculty_workload fw

            INNER JOIN faculty f
                ON fw.faculty_id = f.id

            INNER JOIN classes c
                ON fw.class_id = c.id

            INNER JOIN subjects s
                ON fw.subject_id = s.id

            ORDER BY
                CASE
                    WHEN fw.priority = 'Important' THEN 0
                    ELSE 1
                END,
                fw.periods_per_week DESC,
                fw.id
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# SLOT HELPERS
# ============================================================

def _all_slots():
    """
    Returns all 30 timetable slots.

    6 Day Orders × 5 Periods = 30 slots.
    """

    slots = []

    for day_order in range(1, DAY_ORDERS + 1):
        for period in range(1, PERIODS_PER_DAY + 1):
            slots.append((day_order, period))

    return slots


def _is_adjacent(period1, period2):
    """
    Checks whether two periods are consecutive.
    """

    return abs(period1 - period2) == 1


# ============================================================
# CANDIDATE SCORING
# ============================================================

def _score_slot(
    workload,
    day_order,
    period,
    scheduled
):
    """
    Gives a score to a possible slot.

    Lower score = better slot.

    The scoring intentionally prefers:
        - Different Day Orders
        - Spread-out periods
        - Non-consecutive periods
        - Balanced timetable

    It strongly discourages:
        - Same subject multiple times on same Day Order
        - Consecutive periods of same subject
    """

    workload_id = workload["workload_id"]
    class_id = workload["class_id"]
    faculty_id = workload["faculty_id"]
    subject_id = workload["subject_id"]

    score = 0

    # --------------------------------------------------------
    # Information about this workload already scheduled
    # --------------------------------------------------------

    own_slots = scheduled["workloads"].get(
        workload_id,
        []
    )

    own_days = [
        slot[0]
        for slot in own_slots
    ]

    own_periods = [
        slot[1]
        for slot in own_slots
    ]

    # --------------------------------------------------------
    # MAIN RULE:
    # Spread same subject across different Day Orders.
    # --------------------------------------------------------

    if day_order in own_days:
        score += 1000

    else:
        # New Day Order is strongly preferred.
        score -= 300

    # --------------------------------------------------------
    # If same Day Order is unavoidable,
    # choose a distant period.
    # --------------------------------------------------------

    if own_periods:

        nearest_distance = min(
            abs(period - old_period)
            for old_period in own_periods
        )

        if nearest_distance == 1:
            score += 900

        elif nearest_distance == 2:
            score += 250

        elif nearest_distance >= 3:
            score -= 100

    # --------------------------------------------------------
    # Check same class timetable load for this Day Order.
    # --------------------------------------------------------

    class_day_load = sum(
        1
        for slot_data in scheduled["slots"].values()
        if slot_data["class_id"] == class_id
        and slot_data["day_order"] == day_order
    )

    score += class_day_load * 30

    # --------------------------------------------------------
    # Check faculty timetable load for this Day Order.
    # --------------------------------------------------------

    faculty_day_load = sum(
        1
        for slot_data in scheduled["slots"].values()
        if slot_data["faculty_id"] == faculty_id
        and slot_data["day_order"] == day_order
    )

    score += faculty_day_load * 20

    # --------------------------------------------------------
    # Prefer balanced periods across the Day Order.
    # --------------------------------------------------------

    same_period_count = sum(
        1
        for slot_data in scheduled["slots"].values()
        if slot_data["period"] == period
    )

    score += same_period_count * 2

    # --------------------------------------------------------
    # Slight random factor.
    #
    # This prevents every generation from looking identical.
    # --------------------------------------------------------

    score += random.randint(0, 20)

    return score


# ============================================================
# GENERATE ONE TIMETABLE
# ============================================================

def _generate_once(workloads):
    """
    Attempts to generate one complete timetable.
    """

    scheduled = {
        "slots": {},
        "workloads": {}
    }

    all_slots = _all_slots()

    for workload in workloads:

        workload_id = workload["workload_id"]
        class_id = workload["class_id"]
        faculty_id = workload["faculty_id"]
        subject_id = workload["subject_id"]
        periods_needed = workload["periods_per_week"]

        scheduled["workloads"][workload_id] = []

        for _ in range(periods_needed):

            candidates = []

            for day_order, period in all_slots:

                slot_key = (
                    day_order,
                    period
                )

                # ------------------------------------------------
                # Class clash
                # ------------------------------------------------

                class_clash = any(
                    data["class_id"] == class_id
                    for key, data in scheduled["slots"].items()
                    if key == slot_key
                )

                if class_clash:
                    continue

                # ------------------------------------------------
                # Faculty clash
                # ------------------------------------------------

                faculty_clash = any(
                    data["faculty_id"] == faculty_id
                    for key, data in scheduled["slots"].items()
                    if key == slot_key
                )

                if faculty_clash:
                    continue

                # ------------------------------------------------
                # Same subject should not occupy same slot.
                # ------------------------------------------------

                subject_clash = any(
                    data["subject_id"] == subject_id
                    for key, data in scheduled["slots"].items()
                    if key == slot_key
                )

                if subject_clash:
                    continue

                # ------------------------------------------------
                # Score candidate
                # ------------------------------------------------

                score = _score_slot(
                    workload,
                    day_order,
                    period,
                    scheduled
                )

                candidates.append(
                    (
                        score,
                        day_order,
                        period
                    )
                )

            # ----------------------------------------------------
            # No possible slot
            # ----------------------------------------------------

            if not candidates:
                return None

            # Lowest score = best candidate
            candidates.sort(
                key=lambda item: item[0]
            )

            _, selected_day, selected_period = candidates[0]

            selected_slot = (
                selected_day,
                selected_period
            )

            # ----------------------------------------------------
            # Store timetable entry in memory
            #
            # FIX:
            # day_order and period are stored here because
            # _score_slot() uses them later.
            # ----------------------------------------------------

            scheduled["slots"][selected_slot] = {
                "workload_id": workload_id,
                "day_order": selected_day,
                "period": selected_period,
                "class_id": class_id,
                "subject_id": subject_id,
                "faculty_id": faculty_id
            }

            scheduled["workloads"][workload_id].append(
                selected_slot
            )

    return scheduled


# ============================================================
# VALIDATE GENERATED TIMETABLE
# ============================================================

def _validate_schedule(scheduled, workloads):
    """
    Makes sure every workload received exactly the
    required number of periods.
    """

    for workload in workloads:

        workload_id = workload["workload_id"]
        required = workload["periods_per_week"]

        actual = len(
            scheduled["workloads"].get(
                workload_id,
                []
            )
        )

        if actual != required:
            return False

    return True


# ============================================================
# SAVE GENERATED TIMETABLE
# ============================================================

def _save_timetable(scheduled):
    """
    Saves the generated timetable into SQLite.
    """

    create_timetable_table()

    conn = get_connection()

    try:

        # Remove old generated timetable.
        conn.execute(
            "DELETE FROM timetable"
        )

        for (day_order, period), data in scheduled["slots"].items():

            conn.execute(
                """
                INSERT INTO timetable
                (
                    day_order,
                    period,
                    class_id,
                    subject_id,
                    faculty_id
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    day_order,
                    period,
                    data["class_id"],
                    data["subject_id"],
                    data["faculty_id"]
                )
            )

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# PUBLIC GENERATOR FUNCTION
# ============================================================

def generate_timetable(max_attempts=100):
    """
    Main timetable generation function.

    Returns:
        True  -> successful generation
        False -> generation failed

    Raises:
        ValueError -> invalid workload / impossible timetable
    """

    create_workload_table()
    create_timetable_table()

    raw_workloads = _get_workloads()

    if not raw_workloads:
        raise ValueError(
            "No faculty workload found. "
            "Please add workload before generating timetable."
        )

    workloads = []

    # --------------------------------------------------------
    # Convert database rows into readable dictionaries.
    # --------------------------------------------------------

    for row in raw_workloads:

        (
            workload_id,
            faculty_id,
            class_id,
            subject_id,
            priority,
            periods_per_week,
            faculty_name,
            class_name,
            subject_code,
            subject_name
        ) = row

        if periods_per_week <= 0:
            raise ValueError(
                f"Invalid periods/week for "
                f"{subject_name} ({class_name})."
            )

        # One class cannot have more than 30 periods/week.
        if periods_per_week > TOTAL_SLOTS_PER_CLASS:
            raise ValueError(
                f"{subject_name} requires "
                f"{periods_per_week} periods/week, "
                f"but a class has only "
                f"{TOTAL_SLOTS_PER_CLASS} timetable slots."
            )

        workloads.append(
            {
                "workload_id": workload_id,
                "faculty_id": faculty_id,
                "class_id": class_id,
                "subject_id": subject_id,
                "priority": priority,
                "periods_per_week": periods_per_week,
                "faculty_name": faculty_name,
                "class_name": class_name,
                "subject_code": subject_code,
                "subject_name": subject_name
            }
        )

    # --------------------------------------------------------
    # Check total workload for each class.
    # --------------------------------------------------------

    class_totals = {}

    for workload in workloads:

        class_id = workload["class_id"]

        class_totals[class_id] = (
            class_totals.get(
                class_id,
                0
            )
            + workload["periods_per_week"]
        )

    for class_id, total in class_totals.items():

        if total > TOTAL_SLOTS_PER_CLASS:
            raise ValueError(
                f"One class has {total} required periods/week, "
                f"but only {TOTAL_SLOTS_PER_CLASS} slots are available."
            )

    # --------------------------------------------------------
    # Important workloads first.
    # --------------------------------------------------------

    workloads.sort(
        key=lambda item: (
            0
            if item["priority"] == "Important"
            else 1,
            -item["periods_per_week"],
            item["workload_id"]
        )
    )

    # --------------------------------------------------------
    # Try multiple randomized schedules.
    #
    # This gives different layouts while still following
    # our scheduling rules.
    # --------------------------------------------------------

    for attempt in range(max_attempts):

        attempt_workloads = workloads.copy()

        # Keep Important first, but shuffle workloads
        # inside the same priority group.

        important = [
            w
            for w in attempt_workloads
            if w["priority"] == "Important"
        ]

        normal = [
            w
            for w in attempt_workloads
            if w["priority"] != "Important"
        ]

        random.shuffle(important)
        random.shuffle(normal)

        attempt_workloads = (
            important
            + normal
        )

        scheduled = _generate_once(
            attempt_workloads
        )

        if scheduled is None:
            continue

        if not _validate_schedule(
            scheduled,
            workloads
        ):
            continue

        _save_timetable(
            scheduled
        )

        return True

    raise ValueError(
        "Unable to generate a complete timetable "
        "with the current workload and clash rules. "
        "Please check the workload distribution."
    )


# ============================================================
# GET GENERATED TIMETABLE
# ============================================================

def get_all_timetable():
    """
    Returns the complete generated timetable.
    """

    create_timetable_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                t.id,
                t.day_order,
                t.period,

                t.class_id,
                c.class_name,

                t.subject_id,
                s.subject_code,
                s.subject_name,

                t.faculty_id,
                f.name AS faculty_name

            FROM timetable t

            INNER JOIN classes c
                ON t.class_id = c.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            INNER JOIN faculty f
                ON t.faculty_id = f.id

            ORDER BY
                t.day_order,
                t.period,
                c.class_name
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# CLASS VIEW
# ============================================================

def get_timetable_by_class(class_id):
    """
    Returns timetable from a particular class perspective.
    """

    create_timetable_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                t.day_order,
                t.period,

                c.class_name,

                s.subject_code,
                s.subject_name,

                f.name AS faculty_name

            FROM timetable t

            INNER JOIN classes c
                ON t.class_id = c.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            INNER JOIN faculty f
                ON t.faculty_id = f.id

            WHERE t.class_id = ?

            ORDER BY
                t.day_order,
                t.period
            """,
            (class_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# FACULTY VIEW
# ============================================================

def get_timetable_by_faculty(faculty_id):
    """
    Returns timetable from a particular faculty perspective.
    """

    create_timetable_table()

    conn = get_connection()

    try:

        cursor = conn.execute(
            """
            SELECT
                t.day_order,
                t.period,

                f.name AS faculty_name,

                c.class_name,

                s.subject_code,
                s.subject_name

            FROM timetable t

            INNER JOIN classes c
                ON t.class_id = c.id

            INNER JOIN subjects s
                ON t.subject_id = s.id

            INNER JOIN faculty f
                ON t.faculty_id = f.id

            WHERE t.faculty_id = ?

            ORDER BY
                t.day_order,
                t.period
            """,
            (faculty_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# CLEAR GENERATED TIMETABLE
# ============================================================

def clear_timetable():
    """
    Clears the currently generated timetable.
    """

    create_timetable_table()

    conn = get_connection()

    try:

        conn.execute(
            "DELETE FROM timetable"
        )

        conn.commit()

        return True

    except sqlite3.Error:
        conn.rollback()
        return False

    finally:
        conn.close()


# ============================================================
# AUTO CREATE TABLE
# ============================================================

create_timetable_table()