import random
import re
import sqlite3

from database.database import get_connection
from database.workload import create_workload_table


# ============================================================
# TIMETABLE CONFIGURATION
# ============================================================

DAY_ORDERS = 6
PERIODS_PER_DAY = 5

TOTAL_SLOTS_PER_CLASS = (
    DAY_ORDERS * PERIODS_PER_DAY
)

# Your requirement:
#
# 30 slots per class
# 29 teaching periods
# 1 FREE period
#
REQUIRED_TEACHING_PERIODS = 29

# FREE must always be the last period.
FREE_PERIOD = 5


# ============================================================
# CREATE TIMETABLE TABLE
# ============================================================

def create_timetable_table():
    """
    Creates the generated timetable table.

    IMPORTANT:
    Different classes are allowed to use the same
    Day Order + Period.

    Restrictions are:

        Same class + same slot  -> NOT allowed
        Same faculty + same slot -> NOT allowed

    Therefore the UNIQUE constraints are:

        (day_order, period, class_id)
        (day_order, period, faculty_id)
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
# GET WORKLOADS
# ============================================================

def _get_workloads(target_class_id=None):
    """
    Gets faculty workload assignments (all classes or a specific class).

    Faculty Workload is the source of truth.
    """

    create_workload_table()

    conn = get_connection()

    try:
        where_clause = ""
        params = ()
        if target_class_id is not None:
            where_clause = "WHERE fw.class_id = ?"
            params = (target_class_id,)

        cursor = conn.execute(
            f"""
            SELECT
                fw.id,
                fw.faculty_id,
                fw.class_id,
                fw.subject_id,
                fw.priority,
                fw.periods_per_week,

                f.name,

                c.class_name,
                c.department,
                c.semester,
                c.academic_year,

                s.subject_code,
                s.subject_name

            FROM faculty_workload fw

            INNER JOIN faculty f
                ON fw.faculty_id = f.id

            INNER JOIN classes c
                ON fw.class_id = c.id

            INNER JOIN subjects s
                ON fw.subject_id = s.id

            {where_clause}

            ORDER BY
                fw.class_id,

                CASE
                    WHEN LOWER(TRIM(fw.priority)) = 'important'
                    THEN 0
                    ELSE 1
                END,

                fw.periods_per_week DESC,

                fw.id
            """,
            params
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# YEAR GROUP
# ============================================================

def _get_year_group(
    class_name,
    academic_year
):
    """
    Finds the year group.

    Examples:

        1st BCA -> 1st
        2nd BCA -> 2nd
        3rd BCA -> 3rd

        I BCA   -> 1st
        II BCA  -> 2nd
        III BCA -> 3rd
    """

    if class_name:

        text = str(
            class_name
        ).strip().lower()

        # -----------------------------------------------
        # Normal forms
        # -----------------------------------------------

        match = re.search(
            r"\b(1st|2nd|3rd|4th|5th|6th)\b",
            text
        )

        if match:

            return match.group(1)

        # -----------------------------------------------
        # Roman numeral forms
        # -----------------------------------------------

        roman_match = re.search(
            r"\b(i{1,3}|iv|v|vi)\b",
            text
        )

        if roman_match:

            roman = roman_match.group(1)

            roman_map = {
                "i": "1st",
                "ii": "2nd",
                "iii": "3rd",
                "iv": "4th",
                "v": "5th",
                "vi": "6th"
            }

            return roman_map.get(
                roman,
                roman
            )

    # -----------------------------------------------
    # Fallback
    # -----------------------------------------------

    if academic_year:

        return str(
            academic_year
        ).strip().lower()

    return "unknown"


# ============================================================
# ASSIGN FREE DAY ORDER
# ============================================================

def _assign_free_days(
    class_info,
    randomized=False
):
    """
    Assigns exactly one FREE Day Order to each class.

    FREE is always Period 5.

    Same year:
        3rd BCA -> DO2 P5 FREE
        3rd BSc -> DO2 P5 NOT ALLOWED

    Different year:
        3rd BCA -> DO2 P5 FREE
        2nd BCA -> DO2 P5 FREE ALLOWED
    """

    classes_by_year = {}

    for class_id, info in class_info.items():

        year_group = info[
            "year_group"
        ]

        classes_by_year.setdefault(
            year_group,
            []
        ).append(
            class_id
        )

    # -----------------------------------------------
    # Maximum six classes per year.
    # -----------------------------------------------

    for year_group, class_ids in classes_by_year.items():

        if len(class_ids) > DAY_ORDERS:

            return None

    free_days = {}

    # -----------------------------------------------
    # Assign unique Day Orders inside each year.
    # -----------------------------------------------

    for year_group, class_ids in classes_by_year.items():

        if randomized:
            available_days = list(range(1, DAY_ORDERS + 1))
            random.shuffle(available_days)
            sorted_classes = list(class_ids)
            random.shuffle(sorted_classes)
        else:
            available_days = list(range(DAY_ORDERS, 0, -1))
            sorted_classes = sorted(class_ids)

        for class_id in sorted_classes:
            free_days[class_id] = available_days.pop(0) if available_days else 6

    return free_days


# ============================================================
# CREATE INDIVIDUAL TASKS
# ============================================================

def _build_tasks(
    workloads,
    class_info
):
    """
    Converts workload rows into individual teaching tasks.

    IMPORTANT:

    NO automatic extra periods are created.

    If a class has:

        29 workload periods

    it gets:

        29 teaching tasks.

    If a class has:

        24 workload periods

    this function returns 24 tasks.

    The generator will then reject that class because
    your current timetable design requires:

        29 teaching + 1 FREE.
    """

    workloads_by_class = {}

    for workload in workloads:

        class_id = workload[
            "class_id"
        ]

        workloads_by_class.setdefault(
            class_id,
            []
        ).append(
            workload
        )

    tasks = []

    task_id = 1

    for class_id, class_workloads in workloads_by_class.items():

        total_periods = sum(
            int(
                item[
                    "periods_per_week"
                ]
            )
            for item in class_workloads
        )

        # ------------------------------------------------
        # IMPORTANT:
        # Do NOT add fake/repeated periods.
        # ------------------------------------------------

        if total_periods != REQUIRED_TEACHING_PERIODS:

            class_name = class_info[
                class_id
            ][
                "class_name"
            ]

            raise ValueError(
                f"{class_name} has "
                f"{total_periods} assigned periods/week.\n\n"
                f"This timetable requires exactly "
                f"{REQUIRED_TEACHING_PERIODS} "
                f"teaching periods + 1 FREE period.\n\n"
                f"Please set the workload for this class "
                f"to {REQUIRED_TEACHING_PERIODS} periods."
            )

        # ------------------------------------------------
        # Create actual tasks.
        # ------------------------------------------------

        for workload in class_workloads:

            periods = int(
                workload[
                    "periods_per_week"
                ]
            )

            for occurrence in range(
                periods
            ):

                tasks.append(
                    {
                        "task_id":
                            task_id,

                        "workload_id":
                            workload[
                                "workload_id"
                            ],

                        "class_id":
                            workload[
                                "class_id"
                            ],

                        "faculty_id":
                            workload[
                                "faculty_id"
                            ],

                        "subject_id":
                            workload[
                                "subject_id"
                            ],

                        "priority":
                            workload[
                                "priority"
                            ],

                        "faculty_name":
                            workload[
                                "faculty_name"
                            ],

                        "class_name":
                            workload[
                                "class_name"
                            ],

                        "subject_code":
                            workload[
                                "subject_code"
                            ],

                        "subject_name":
                            workload[
                                "subject_name"
                            ],

                        "occurrence":
                            occurrence
                    }
                )

                task_id += 1

    return tasks


# ============================================================
# GROUP TASKS BY CLASS
# ============================================================

def _group_tasks_by_class(
    tasks
):
    """
    Groups teaching tasks by class.
    """

    result = {}

    for task in tasks:

        class_id = task[
            "class_id"
        ]

        result.setdefault(
            class_id,
            []
        ).append(
            task
        )

    return result


# ============================================================
# ALL 30 SLOTS
# ============================================================

def _all_slots():
    """
    Returns all 30 slots.

    Example:

        (1,1)
        (1,2)
        ...
        (6,5)
    """

    slots = []

    for day_order in range(
        1,
        DAY_ORDERS + 1
    ):

        for period in range(
            1,
            PERIODS_PER_DAY + 1
        ):

            slots.append(
                (
                    day_order,
                    period
                )
            )

    return slots


# ============================================================
# CLASS TEACHING SLOTS
# ============================================================

def _get_class_teaching_slots(
    free_day
):
    """
    Returns the 29 usable teaching slots.

    The only excluded slot is:

        FREE DAY + Period 5
    """

    slots = []

    for day_order in range(
        1,
        DAY_ORDERS + 1
    ):

        for period in range(
            1,
            PERIODS_PER_DAY + 1
        ):

            if (
                day_order == free_day
                and period == FREE_PERIOD
            ):
                continue

            slots.append(
                (
                    day_order,
                    period
                )
            )

    return slots


# ============================================================
# SLOT AVAILABILITY
# ============================================================

def _faculty_is_free(
    faculty_busy,
    faculty_id,
    day_order,
    period
):
    """
    Checks whether faculty is available.
    """

    return (
        day_order,
        period,
        faculty_id
    ) not in faculty_busy


# ============================================================
# SUBJECT HISTORY
# ============================================================

def _get_subject_history(
    class_schedule,
    subject_id
):
    """
    Returns previous slots for a subject
    inside one class.
    """

    result = []

    for data in class_schedule:

        if data[
            "subject_id"
        ] == subject_id:

            result.append(
                (
                    data[
                        "day_order"
                    ],

                    data[
                        "period"
                    ]
                )
            )

    return result


# ============================================================
# SCORE A SLOT
# ============================================================

def _score_candidate(
    task,
    day_order,
    period,
    class_schedule
):
    """
    Gives a score to a possible slot.

    Lower score = better.

    This is a SOFT scoring system.

    Hard constraints are handled separately:

        - class conflict
        - faculty conflict
        - FREE slot
    """

    subject_id = task[
        "subject_id"
    ]

    score = 0

    subject_history = _get_subject_history(
        class_schedule,
        subject_id
    )

    subject_days = [
        item[0]
        for item in subject_history
    ]

    # ------------------------------------------------
    # Prefer distributing subject across Day Orders.
    # ------------------------------------------------

    if day_order in subject_days:

        score += 500

    else:

        score -= 150

    # ------------------------------------------------
    # Avoid consecutive same subject.
    # ------------------------------------------------

    for old_day, old_period in subject_history:

        if old_day != day_order:
            continue

        difference = abs(
            old_period - period
        )

        if difference == 1:

            score += 1000

        elif difference == 2:

            score += 200

        elif difference >= 3:

            score -= 20

    # ------------------------------------------------
    # Balance number of periods in each day.
    # ------------------------------------------------

    day_load = sum(
        1
        for item in class_schedule
        if item[
            "day_order"
        ] == day_order
    )

    score += (
        day_load * 20
    )

    # ------------------------------------------------
    # Important subjects get preference for prime morning periods.
    # ------------------------------------------------

    is_important = str(task.get("priority", "")).strip().lower() == "important"
    if is_important:
        score += (period - 1) * 35
    else:
        score += (5 - period) * 10

    # Deterministic tie-breaker based on day and period
    score += (day_order * 2 + period)

    return score


# ============================================================
# PLACE ONE CLASS
# ============================================================

def _schedule_class(
    class_id,
    class_tasks,
    free_day,
    faculty_busy,
    mode="efficient"
):
    """
    Schedules exactly one class.

    This function allows other classes to use
    the SAME Day Order + Period.

    Only faculty conflicts are checked globally.
    Supports 'efficient' (structured constraint optimization) and 'random' (varied stochastic) modes.
    """
    is_random = (mode == "random")
    teaching_slots = _get_class_teaching_slots(
        free_day
    )
    if is_random:
        teaching_slots = list(teaching_slots)
        random.shuffle(teaching_slots)

    # -----------------------------------------------
    # Local class schedule.
    # -----------------------------------------------

    class_schedule = []

    used_slots = set()

    # -----------------------------------------------
    # Copy tasks.
    # -----------------------------------------------

    remaining_tasks = list(
        class_tasks
    )

    if is_random:
        random.shuffle(remaining_tasks)
    else:
        # Sort deterministically: Important first, then higher periods/week, then subject ID
        remaining_tasks.sort(
            key=lambda t: (
                0 if str(t.get("priority", "")).strip().lower() == "important" else 1,
                -int(t.get("periods_per_week", 0)),
                int(t.get("subject_id", 0)),
                int(t.get("task_id", 0))
            )
        )

    # -----------------------------------------------
    # Recursive backtracking.
    # -----------------------------------------------

    def backtrack(
        tasks_left
    ):

        # -------------------------------------------
        # Everything scheduled.
        # -------------------------------------------

        if not tasks_left:

            return True

        # -------------------------------------------
        # Find the task with the fewest available
        # slots (MRV = Minimum Remaining Values).
        # -------------------------------------------

        best_task = None
        best_candidates = None

        for task in tasks_left:

            candidates = []

            for day_order, period in teaching_slots:

                key = (
                    day_order,
                    period
                )

                # Slot already used by this class.
                if key in used_slots:
                    continue

                # Faculty conflict.
                if not _faculty_is_free(
                    faculty_busy,
                    task[
                        "faculty_id"
                    ],
                    day_order,
                    period
                ):
                    continue

                base_score = _score_candidate(
                    task,
                    day_order,
                    period,
                    class_schedule
                )
                score = base_score + (random.randint(-400, 400) if is_random else 0)

                candidates.append(
                    (
                        score,
                        day_order,
                        period
                    )
                )

            # ---------------------------------------
            # No slot for this task.
            # ---------------------------------------

            if not candidates:

                return False

            # ---------------------------------------
            # Choose the most constrained task.
            # ---------------------------------------

            if (
                best_candidates is None
                or len(candidates)
                < len(best_candidates)
            ):

                best_task = task
                best_candidates = candidates

            elif (
                len(candidates)
                == len(best_candidates)
            ):

                # Important task wins tie.
                current_important = (
                    str(
                        task[
                            "priority"
                        ]
                    ).strip().lower()
                    == "important"
                )

                best_important = (
                    str(
                        best_task[
                            "priority"
                        ]
                    ).strip().lower()
                    == "important"
                )

                if (
                    current_important
                    and not best_important
                ):

                    best_task = task
                    best_candidates = candidates

        # -------------------------------------------
        # Sort candidate slots.
        # -------------------------------------------

        best_candidates.sort(
            key=lambda item: item[0]
        )

        # -------------------------------------------
        # Keep top candidates.
        # -------------------------------------------

        candidate_limit = min(
            len(best_candidates),
            12
        )

        selected_candidates = list(
            best_candidates[
                :candidate_limit
            ]
        )
        if is_random:
            random.shuffle(selected_candidates)

        # -------------------------------------------
        # Try candidates.
        # -------------------------------------------

        for (
            score,
            day_order,
            period
        ) in selected_candidates:

            key = (
                day_order,
                period
            )

            # ---------------------------------------
            # Place.
            # ---------------------------------------

            used_slots.add(
                key
            )

            faculty_key = (
                day_order,
                period,
                best_task[
                    "faculty_id"
                ]
            )

            faculty_busy.add(
                faculty_key
            )

            entry = {
                "task_id":
                    best_task[
                        "task_id"
                    ],

                "workload_id":
                    best_task[
                        "workload_id"
                    ],

                "day_order":
                    day_order,

                "period":
                    period,

                "class_id":
                    class_id,

                "subject_id":
                    best_task[
                        "subject_id"
                    ],

                "faculty_id":
                    best_task[
                        "faculty_id"
                    ]
            }

            class_schedule.append(
                entry
            )

            # ---------------------------------------
            # Continue.
            # ---------------------------------------

            next_tasks = [
                task
                for task in tasks_left
                if task[
                    "task_id"
                ]
                != best_task[
                    "task_id"
                ]
            ]

            if backtrack(
                next_tasks
            ):

                return True

            # ---------------------------------------
            # Undo.
            # ---------------------------------------

            class_schedule.pop()

            faculty_busy.discard(
                faculty_key
            )

            used_slots.discard(
                key
            )

        return False

    # -----------------------------------------------
    # Start.
    # -----------------------------------------------

    success = backtrack(
        remaining_tasks
    )

    if not success:

        return None

    return class_schedule


# ============================================================
# GENERATE COMPLETE TIMETABLE
# ============================================================

def _generate_once(
    tasks,
    class_info,
    free_days,
    mode="efficient"
):
    """
    Generates one complete timetable.

    KEY DIFFERENCE FROM OLD VERSION:

    The schedule key includes class_id.

    Therefore:

        DO1 P1 BCA
        DO1 P1 BCOM

    are both allowed.

    Only faculty conflicts are prevented.
    """

    tasks_by_class = _group_tasks_by_class(
        tasks
    )

    # -----------------------------------------------
    # Faculty workload count.
    # Used to determine difficult classes.
    # -----------------------------------------------

    faculty_total = {}

    for task in tasks:

        faculty_id = task[
            "faculty_id"
        ]

        faculty_total[
            faculty_id
        ] = (
            faculty_total.get(
                faculty_id,
                0
            )
            + 1
        )

    # -----------------------------------------------
    # Calculate class difficulty.
    #
    # Classes sharing heavily-used faculty are
    # scheduled first.
    # -----------------------------------------------

    class_priority = {}

    for class_id, class_tasks in tasks_by_class.items():

        score = 0

        faculty_counts = {}

        for task in class_tasks:

            faculty_id = task[
                "faculty_id"
            ]

            faculty_counts[
                faculty_id
            ] = (
                faculty_counts.get(
                    faculty_id,
                    0
                )
                + 1
            )

        for faculty_id, count in faculty_counts.items():

            score += (
                count
                * faculty_total.get(
                    faculty_id,
                    0
                )
            )

        # Important workload increases priority.
        for task in class_tasks:

            if str(
                task[
                    "priority"
                ]
            ).strip().lower() == "important":

                score += 10

        class_priority[
            class_id
        ] = score

    # -----------------------------------------------
    # Randomize ties or class order based on mode.
    # -----------------------------------------------

    class_ids = list(
        tasks_by_class.keys()
    )

    if mode == "random":
        random.shuffle(class_ids)
    else:
        # Sort deterministically by constraint tightness score descending, break ties with class_id
        class_ids.sort(
            key=lambda cid: (
                class_priority.get(cid, 0),
                -cid
            ),
            reverse=True
        )

    # -----------------------------------------------
    # GLOBAL FACULTY BUSY SET
    #
    # This is the ONLY global slot restriction.
    #
    # Different classes may use the same slot.
    # -----------------------------------------------

    faculty_busy = set()

    all_entries = []

    # -----------------------------------------------
    # Schedule classes one by one.
    # -----------------------------------------------

    for class_id in class_ids:

        result = _schedule_class(
            class_id,
            tasks_by_class[
                class_id
            ],
            free_days[
                class_id
            ],
            faculty_busy,
            mode=mode
        )

        if result is None:

            return None

        all_entries.extend(
            result
        )

    # -----------------------------------------------
    # Convert to timetable dictionary.
    #
    # IMPORTANT:
    #
    # key = (day, period, class_id)
    #
    # NOT:
    #
    # key = (day, period)
    #
    # This is the critical bug fix.
    # -----------------------------------------------

    timetable = {}

    for entry in all_entries:

        key = (
            entry[
                "day_order"
            ],

            entry[
                "period"
            ],

            entry[
                "class_id"
            ]
        )

        timetable[
            key
        ] = entry

    return timetable


# ============================================================
# VALIDATE COMPLETE TIMETABLE
# ============================================================

def _validate_schedule(
    timetable,
    class_info,
    free_days
):
    """
    Performs final validation.

    Rules:

        1. Every class has exactly 29 teaching periods.
        2. Every class has exactly one FREE.
        3. FREE is Period 5.
        4. Same-year classes have different FREE Day Orders.
        5. No class clash.
        6. No faculty clash.
    """

    # ========================================================
    # CLASS VALIDATION
    # ========================================================

    for class_id in class_info:

        entries = [
            data
            for data in timetable.values()
            if data[
                "class_id"
            ] == class_id
        ]

        # -----------------------------------------------
        # Exactly 29 teaching periods.
        # -----------------------------------------------

        if len(
            entries
        ) != REQUIRED_TEACHING_PERIODS:

            return False

        # -----------------------------------------------
        # Expected teaching slots.
        # -----------------------------------------------

        expected_slots = set(
            _get_class_teaching_slots(
                free_days[
                    class_id
                ]
            )
        )

        actual_slots = {
            (
                data[
                    "day_order"
                ],

                data[
                    "period"
                ]
            )
            for data in entries
        }

        if actual_slots != expected_slots:

            return False

        # -----------------------------------------------
        # FREE must be Day Order + Period 5.
        # -----------------------------------------------

        free_slot = (
            free_days[
                class_id
            ],

            FREE_PERIOD
        )

        if free_slot in actual_slots:

            return False

    # ========================================================
    # FACULTY CLASH CHECK
    # ========================================================

    faculty_slots = set()

    for data in timetable.values():

        key = (
            data[
                "day_order"
            ],

            data[
                "period"
            ],

            data[
                "faculty_id"
            ]
        )

        if key in faculty_slots:

            return False

        faculty_slots.add(
            key
        )

    # ========================================================
    # CLASS CLASH CHECK
    # ========================================================

    class_slots = set()

    for data in timetable.values():

        key = (
            data[
                "day_order"
            ],

            data[
                "period"
            ],

            data[
                "class_id"
            ]
        )

        if key in class_slots:

            return False

        class_slots.add(
            key
        )

    # ========================================================
    # SAME-YEAR FREE DAY CHECK
    # ========================================================

    free_days_by_year = {}

    for class_id, info in class_info.items():

        year_group = info[
            "year_group"
        ]

        free_day = free_days[
            class_id
        ]

        free_days_by_year.setdefault(
            year_group,
            set()
        )

        if free_day in free_days_by_year[
            year_group
        ]:

            return False

        free_days_by_year[
            year_group
        ].add(
            free_day
        )

    return True


# ============================================================
# SAVE TIMETABLE
# ============================================================

def _save_timetable(
    timetable,
    target_class_id=None
):
    """
    Saves generated timetable (either whole database or for a specific target class).

    Different classes may have the same
    Day Order + Period.

    Faculty conflicts are prevented before saving.
    """

    create_timetable_table()

    conn = get_connection()

    try:

        # -----------------------------------------------
        # Remove old generated timetable for target class or all.
        # -----------------------------------------------

        if target_class_id is not None:
            conn.execute(
                "DELETE FROM timetable WHERE class_id = ?",
                (target_class_id,)
            )
        else:
            conn.execute(
                "DELETE FROM timetable"
            )

        # -----------------------------------------------
        # Insert new timetable.
        # -----------------------------------------------

        for data in timetable.values():

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
                    data[
                        "day_order"
                    ],

                    data[
                        "period"
                    ],

                    data[
                        "class_id"
                    ],

                    data[
                        "subject_id"
                    ],

                    data[
                        "faculty_id"
                    ]
                )
            )

        conn.commit()

    except sqlite3.Error as error:

        conn.rollback()

        raise ValueError(
            f"Unable to save timetable:\n{error}"
        )

    finally:

        conn.close()


# ============================================================
# PUBLIC GENERATE FUNCTION
# ============================================================

def generate_timetable(
    max_attempts=300,
    target_class_id=None,
    mode="efficient"
):
    if target_class_id is not None:
        return generate_timetable_for_class(target_class_id, max_attempts=max_attempts, mode=mode)
    """
    Main timetable generation function.

    FINAL RULE:

        Each class:
            29 teaching periods
            1 FREE period

        FREE:
            Period 5 only

        Same year:
            FREE Day Order must be unique

        Different classes:
            SAME Day Order + Period is allowed

        Faculty:
            SAME Day Order + Period is NOT allowed
    """

    create_workload_table()
    create_timetable_table()

    # ========================================================
    # GET WORKLOAD
    # ========================================================

    raw_workloads = _get_workloads()

    if not raw_workloads:

        raise ValueError(
            "No faculty workload found.\n\n"
            "Please add Faculty Workload first."
        )

    workloads = []

    class_info = {}

    # ========================================================
    # CONVERT DATABASE ROWS
    # ========================================================

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
            department,
            semester,
            academic_year,

            subject_code,
            subject_name
        ) = row

        periods_per_week = int(
            periods_per_week
        )

        if periods_per_week <= 0:

            raise ValueError(
                f"Invalid periods/week:\n"
                f"{subject_name}\n"
                f"{class_name}"
            )

        workload = {
            "workload_id":
                workload_id,

            "faculty_id":
                faculty_id,

            "class_id":
                class_id,

            "subject_id":
                subject_id,

            "priority":
                priority,

            "periods_per_week":
                periods_per_week,

            "faculty_name":
                faculty_name,

            "class_name":
                class_name,

            "department":
                department,

            "semester":
                semester,

            "academic_year":
                academic_year,

            "subject_code":
                subject_code,

            "subject_name":
                subject_name
        }

        workloads.append(
            workload
        )

        # -----------------------------------------------
        # Store class information.
        # -----------------------------------------------

        if class_id not in class_info:

            class_info[
                class_id
            ] = {
                "class_name":
                    class_name,

                "department":
                    department,

                "semester":
                    semester,

                "academic_year":
                    academic_year,

                "year_group":
                    _get_year_group(
                        class_name,
                        academic_year
                    )
            }

    # ========================================================
    # SHOW CLASS-WISE WORKLOAD
    # ========================================================

    class_totals = {}

    for workload in workloads:

        class_id = workload[
            "class_id"
        ]

        class_totals[
            class_id
        ] = (
            class_totals.get(
                class_id,
                0
            )
            + workload[
                "periods_per_week"
            ]
        )

    # ========================================================
    # CRITICAL VALIDATION:
    #
    # DO NOT compare TOTAL of all classes with 29.
    #
    # Compare EACH class individually.
    # ========================================================

    invalid_classes = []

    for class_id, info in class_info.items():

        total = class_totals.get(
            class_id,
            0
        )

        if total != REQUIRED_TEACHING_PERIODS:

            invalid_classes.append(
                (
                    info[
                        "class_name"
                    ],

                    total
                )
            )

    if invalid_classes:

        details = "\n".join(
            [
                f"• {class_name}: "
                f"{total} periods assigned"
                for class_name, total
                in invalid_classes
            ]
        )

        raise ValueError(
            "Every class must have exactly "
            f"{REQUIRED_TEACHING_PERIODS} "
            "assigned teaching periods.\n\n"
            "Current class-wise workload:\n"
            f"{details}\n\n"
            "IMPORTANT:\n"
            "The total of all classes can be greater "
            "than 29. That is completely valid.\n\n"
            "Example:\n"
            "BCA = 29\n"
            "BCOM = 29\n"
            "Total = 58"
        )

    # ========================================================
    # BUILD TASKS
    # ========================================================

    try:

        tasks = _build_tasks(
            workloads,
            class_info
        )

    except ValueError:

        raise

    # ========================================================
    # CHECK FACULTY TOTAL CAPACITY
    # ========================================================

    faculty_totals = {}

    faculty_names = {}

    for task in tasks:

        faculty_id = task[
            "faculty_id"
        ]

        faculty_totals[
            faculty_id
        ] = (
            faculty_totals.get(
                faculty_id,
                0
            )
            + 1
        )

        faculty_names[
            faculty_id
        ] = task[
            "faculty_name"
        ]

    overloaded = []

    for faculty_id, total in faculty_totals.items():

        # One faculty cannot teach more than
        # 30 periods in a 6 x 5 timetable.
        if total > TOTAL_SLOTS_PER_CLASS:

            overloaded.append(
                f"• {faculty_names[faculty_id]}: "
                f"{total} periods"
            )

    if overloaded:

        raise ValueError(
            "Faculty workload conflict detected.\n\n"
            "The following faculty members have more "
            "than 30 assigned periods:\n\n"
            + "\n".join(
                overloaded
            )
        )

    # ========================================================
    # CHECK SAME-YEAR CLASS COUNT
    # ========================================================

    classes_by_year = {}

    for class_id, info in class_info.items():

        year_group = info[
            "year_group"
        ]

        classes_by_year.setdefault(
            year_group,
            []
        ).append(
            class_id
        )

    for year_group, class_ids in classes_by_year.items():

        if len(
            class_ids
        ) > DAY_ORDERS:

            names = [
                class_info[
                    cid
                ][
                    "class_name"
                ]
                for cid in class_ids
            ]

            raise ValueError(
                f"Year group '{year_group}' has "
                f"{len(class_ids)} classes.\n\n"
                f"Classes:\n"
                + "\n".join(
                    f"• {name}"
                    for name in names
                )
                + "\n\n"
                f"Only {DAY_ORDERS} Day Orders are "
                "available for unique FREE periods."
            )

    # ========================================================
    # GENERATION ATTEMPTS
    # ========================================================

    for attempt in range(
        1,
        max_attempts + 1
    ):

        # -----------------------------------------------
        # Assign FREE Day Orders.
        # -----------------------------------------------

        free_days = _assign_free_days(
            class_info,
            randomized=(mode == "random")
        )

        if free_days is None:

            continue

        # -----------------------------------------------
        # Generate.
        # -----------------------------------------------

        timetable = _generate_once(
            tasks,
            class_info,
            free_days,
            mode=mode
        )

        if timetable is None:

            continue

        # -----------------------------------------------
        # Validate.
        # -----------------------------------------------

        if not _validate_schedule(
            timetable,
            class_info,
            free_days
        ):

            continue

        # -----------------------------------------------
        # Save.
        # -----------------------------------------------

        _save_timetable(
            timetable
        )

        return True

    # ========================================================
    # FAILED
    # ========================================================

    raise ValueError(
        "Unable to generate the timetable "
        f"after {max_attempts} attempts.\n\n"

        "The class-wise workload totals are valid, "
        "but the faculty assignments could not be "
        "placed without a faculty clash.\n\n"

        "Rules checked:\n"
        "• 29 teaching periods per class\n"
        "• 1 FREE period per class\n"
        "• FREE is Period 5\n"
        "• Same-year classes have different FREE Day Orders\n"
        "• Different classes may share the same Day/Period\n"
        "• Same faculty cannot teach two classes at once\n"
        "• Same class cannot have two subjects at once"
    )


# ============================================================
# GET ALL TIMETABLE
# ============================================================

def get_all_timetable():
    """
    Returns all generated timetable entries.
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
                t.class_id,
                t.day_order,
                t.period
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# GET TIMETABLE BY CLASS
# ============================================================

def get_timetable_by_class(
    class_id
):
    """
    Returns timetable for one class.

    The View Timetable UI can use this to switch
    between classes.
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

                f.name AS faculty_name,
                c.semester AS class_semester,
                s.semester AS subject_semester

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
            (
                class_id,
            )
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# GET TIMETABLE BY FACULTY
# ============================================================

def get_timetable_by_faculty(
    faculty_id
):
    """
    Returns timetable for one faculty member.
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
                s.subject_name,
                c.semester AS class_semester,
                s.semester AS subject_semester

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
            (
                faculty_id,
            )
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ============================================================
# CLEAR TIMETABLE
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
# CREATE TABLE ON IMPORT
# ============================================================

create_timetable_table()

# ============================================================
# GENERATE FOR SINGLE CLASS
# ============================================================

def generate_timetable_for_class(
    target_class_id,
    max_attempts=300,
    mode="efficient"
):
    """
    Generates or regenerates timetable for a single specific class.
    Leaves all other classes' timetables in place, and ensures
    no faculty clashes against already-scheduled classes.
    """
    create_workload_table()
    create_timetable_table()

    raw_workloads = _get_workloads(target_class_id=target_class_id)
    if not raw_workloads:
        raise ValueError(
            "No faculty workload found for the selected class.\n\n"
            "Please assign faculty workload for this class first."
        )

    workloads = []
    class_info = {}

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
            department,
            semester,
            academic_year,
            subject_code,
            subject_name
        ) = row

        periods_per_week = int(periods_per_week)
        if periods_per_week <= 0:
            raise ValueError(f"Invalid periods/week for subject {subject_name}")

        workload = {
            "workload_id": workload_id,
            "faculty_id": faculty_id,
            "class_id": class_id,
            "subject_id": subject_id,
            "priority": priority,
            "periods_per_week": periods_per_week,
            "faculty_name": faculty_name,
            "class_name": class_name,
            "department": department,
            "semester": semester,
            "academic_year": academic_year,
            "subject_code": subject_code,
            "subject_name": subject_name
        }
        workloads.append(workload)
        if class_id not in class_info:
            class_info[class_id] = {
                "class_name": class_name,
                "department": department,
                "semester": semester,
                "academic_year": academic_year,
                "year_group": _get_year_group(class_name, academic_year)
            }

    total_periods = sum(w["periods_per_week"] for w in workloads)
    if total_periods != REQUIRED_TEACHING_PERIODS:
        cname = class_info[target_class_id]["class_name"]
        raise ValueError(
            f"The selected class '{cname}' has {total_periods} periods assigned.\n\n"
            f"It must have exactly {REQUIRED_TEACHING_PERIODS} teaching periods to generate a valid timetable."
        )

    tasks = _build_tasks(workloads, class_info)

    # Load existing commitments of faculty from other classes
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT t.day_order, t.period, t.faculty_id, t.class_id, c.class_name, c.academic_year
            FROM timetable t
            INNER JOIN classes c ON t.class_id = c.id
            WHERE t.class_id != ?
            """,
            (target_class_id,)
        )
        existing_rows = cursor.fetchall()
    finally:
        conn.close()

    existing_faculty_busy = {(r[0], r[1], r[2]) for r in existing_rows}

    # Find used free days for same-year classes
    target_year = class_info[target_class_id]["year_group"]
    used_same_year_free_days = set()

    other_classes_slots = {}
    for r in existing_rows:
        day_o, per, fac, cid, cname, ac_yr = r
        other_classes_slots.setdefault(cid, {"year_group": _get_year_group(cname, ac_yr), "p5_days": set()})
        if per == FREE_PERIOD:
            other_classes_slots[cid]["p5_days"].add(day_o)

    for cid, cdata in other_classes_slots.items():
        if cdata["year_group"] == target_year:
            missing_p5 = set(range(1, DAY_ORDERS + 1)) - cdata["p5_days"]
            if missing_p5:
                used_same_year_free_days.add(next(iter(missing_p5)))

    available_free_days = [d for d in range(1, DAY_ORDERS + 1) if d not in used_same_year_free_days]
    if not available_free_days:
        available_free_days = list(range(1, DAY_ORDERS + 1))

    if mode == "random":
        available_free_days = list(available_free_days)
        random.shuffle(available_free_days)

    for attempt in range(1, max_attempts + 1):
        free_day = available_free_days[attempt % len(available_free_days)]
        faculty_busy = set(existing_faculty_busy)

        class_result = _schedule_class(
            target_class_id,
            tasks,
            free_day,
            faculty_busy,
            mode=mode
        )

        if class_result is None:
            continue

        timetable_dict = {}
        for entry in class_result:
            key = (entry["day_order"], entry["period"], entry["class_id"])
            timetable_dict[key] = entry

        _save_timetable(timetable_dict, target_class_id=target_class_id)
        return True

    cname = class_info[target_class_id]["class_name"]
    raise ValueError(
        f"Unable to generate schedule for '{cname}' without faculty conflicts against existing classes after {max_attempts} attempts.\n\n"
        f"Please check faculty assignments or adjust workload."
    )
