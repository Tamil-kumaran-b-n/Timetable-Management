import random
import re
import sqlite3
from database.database import get_connection
from database.workload import create_workload_table
DAY_ORDERS = 6
PERIODS_PER_DAY = 5
TOTAL_SLOTS_PER_CLASS = DAY_ORDERS * PERIODS_PER_DAY
REQUIRED_TEACHING_PERIODS = 29
FREE_PERIOD = 5

def create_timetable_table():
    conn = get_connection()
    try:
        conn.execute('\n            CREATE TABLE IF NOT EXISTS timetable\n            (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n\n                day_order INTEGER NOT NULL,\n                period INTEGER NOT NULL,\n\n                class_id INTEGER NOT NULL,\n                subject_id INTEGER NOT NULL,\n                faculty_id INTEGER NOT NULL,\n\n                UNIQUE(day_order, period, class_id),\n                UNIQUE(day_order, period, faculty_id),\n\n                FOREIGN KEY (class_id)\n                    REFERENCES classes(id)\n                    ON DELETE CASCADE,\n\n                FOREIGN KEY (subject_id)\n                    REFERENCES subjects(id)\n                    ON DELETE CASCADE,\n\n                FOREIGN KEY (faculty_id)\n                    REFERENCES faculty(id)\n                    ON DELETE CASCADE\n            )\n            ')
        conn.commit()
    finally:
        conn.close()

def _get_workloads(target_class_id=None):
    create_workload_table()
    conn = get_connection()
    try:
        where_clause = ''
        params = ()
        if target_class_id is not None:
            where_clause = 'WHERE fw.class_id = ?'
            params = (target_class_id,)
        cursor = conn.execute(f"\n            SELECT\n                fw.id,\n                fw.faculty_id,\n                fw.class_id,\n                fw.subject_id,\n                fw.priority,\n                fw.periods_per_week,\n\n                f.name,\n\n                c.class_name,\n                c.department,\n                c.semester,\n                c.academic_year,\n\n                s.subject_code,\n                s.subject_name\n\n            FROM faculty_workload fw\n\n            INNER JOIN faculty f\n                ON fw.faculty_id = f.id\n\n            INNER JOIN classes c\n                ON fw.class_id = c.id\n\n            INNER JOIN subjects s\n                ON fw.subject_id = s.id\n\n            {where_clause}\n\n            ORDER BY\n                fw.class_id,\n\n                CASE\n                    WHEN LOWER(TRIM(fw.priority)) = 'important'\n                    THEN 0\n                    ELSE 1\n                END,\n\n                fw.periods_per_week DESC,\n\n                fw.id\n            ", params)
        return cursor.fetchall()
    finally:
        conn.close()

def _get_year_group(class_name, academic_year):
    if class_name:
        text = str(class_name).strip().lower()
        match = re.search('\\b(1st|2nd|3rd|4th|5th|6th)\\b', text)
        if match:
            return match.group(1)
        roman_match = re.search('\\b(i{1,3}|iv|v|vi)\\b', text)
        if roman_match:
            roman = roman_match.group(1)
            roman_map = {'i': '1st', 'ii': '2nd', 'iii': '3rd', 'iv': '4th', 'v': '5th', 'vi': '6th'}
            return roman_map.get(roman, roman)
    if academic_year:
        return str(academic_year).strip().lower()
    return 'unknown'

def _assign_free_days(class_info, randomized=False):
    classes_by_year = {}
    for class_id, info in class_info.items():
        year_group = info['year_group']
        classes_by_year.setdefault(year_group, []).append(class_id)
    for year_group, class_ids in classes_by_year.items():
        if len(class_ids) > DAY_ORDERS:
            return None
    free_days = {}
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

def _build_tasks(workloads, class_info):
    workloads_by_class = {}
    for workload in workloads:
        class_id = workload['class_id']
        workloads_by_class.setdefault(class_id, []).append(workload)
    tasks = []
    task_id = 1
    for class_id, class_workloads in workloads_by_class.items():
        total_periods = sum((int(item['periods_per_week']) for item in class_workloads))
        if total_periods != REQUIRED_TEACHING_PERIODS:
            class_name = class_info[class_id]['class_name']
            raise ValueError(f'{class_name} has {total_periods} assigned periods/week.\n\nThis timetable requires exactly {REQUIRED_TEACHING_PERIODS} teaching periods + 1 FREE period.\n\nPlease set the workload for this class to {REQUIRED_TEACHING_PERIODS} periods.')
        for workload in class_workloads:
            periods = int(workload['periods_per_week'])
            for occurrence in range(periods):
                tasks.append({'task_id': task_id, 'workload_id': workload['workload_id'], 'class_id': workload['class_id'], 'faculty_id': workload['faculty_id'], 'subject_id': workload['subject_id'], 'priority': workload['priority'], 'faculty_name': workload['faculty_name'], 'class_name': workload['class_name'], 'subject_code': workload['subject_code'], 'subject_name': workload['subject_name'], 'occurrence': occurrence})
                task_id += 1
    return tasks

def _group_tasks_by_class(tasks):
    result = {}
    for task in tasks:
        class_id = task['class_id']
        result.setdefault(class_id, []).append(task)
    return result

def _all_slots():
    slots = []
    for day_order in range(1, DAY_ORDERS + 1):
        for period in range(1, PERIODS_PER_DAY + 1):
            slots.append((day_order, period))
    return slots

def _get_class_teaching_slots(free_day):
    slots = []
    for day_order in range(1, DAY_ORDERS + 1):
        for period in range(1, PERIODS_PER_DAY + 1):
            if day_order == free_day and period == FREE_PERIOD:
                continue
            slots.append((day_order, period))
    return slots

def _faculty_is_free(faculty_busy, faculty_id, day_order, period):
    return (day_order, period, faculty_id) not in faculty_busy

def _get_subject_history(class_schedule, subject_id):
    result = []
    for data in class_schedule:
        if data['subject_id'] == subject_id:
            result.append((data['day_order'], data['period']))
    return result

def _score_candidate(task, day_order, period, class_schedule):
    subject_id = task['subject_id']
    score = 0
    subject_history = _get_subject_history(class_schedule, subject_id)
    subject_days = [item[0] for item in subject_history]
    if day_order in subject_days:
        score += 500
    else:
        score -= 150
    for old_day, old_period in subject_history:
        if old_day != day_order:
            continue
        difference = abs(old_period - period)
        if difference == 1:
            score += 1000
        elif difference == 2:
            score += 200
        elif difference >= 3:
            score -= 20
    day_load = sum((1 for item in class_schedule if item['day_order'] == day_order))
    score += day_load * 20
    is_important = str(task.get('priority', '')).strip().lower() == 'important'
    if is_important:
        score += (period - 1) * 35
    else:
        score += (5 - period) * 10
    score += day_order * 2 + period
    return score

def _schedule_class(class_id, class_tasks, free_day, faculty_busy, mode='efficient'):
    is_random = mode == 'random'
    teaching_slots = _get_class_teaching_slots(free_day)
    if is_random:
        teaching_slots = list(teaching_slots)
        random.shuffle(teaching_slots)
    class_schedule = []
    used_slots = set()
    remaining_tasks = list(class_tasks)
    if is_random:
        random.shuffle(remaining_tasks)
    else:
        remaining_tasks.sort(key=lambda t: (0 if str(t.get('priority', '')).strip().lower() == 'important' else 1, -int(t.get('periods_per_week', 0)), int(t.get('subject_id', 0)), int(t.get('task_id', 0))))

    def backtrack(tasks_left):
        if not tasks_left:
            return True
        best_task = None
        best_candidates = None
        for task in tasks_left:
            candidates = []
            for day_order, period in teaching_slots:
                key = (day_order, period)
                if key in used_slots:
                    continue
                if not _faculty_is_free(faculty_busy, task['faculty_id'], day_order, period):
                    continue
                base_score = _score_candidate(task, day_order, period, class_schedule)
                score = base_score + (random.randint(-400, 400) if is_random else 0)
                candidates.append((score, day_order, period))
            if not candidates:
                return False
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_task = task
                best_candidates = candidates
            elif len(candidates) == len(best_candidates):
                current_important = str(task['priority']).strip().lower() == 'important'
                best_important = str(best_task['priority']).strip().lower() == 'important'
                if current_important and (not best_important):
                    best_task = task
                    best_candidates = candidates
        best_candidates.sort(key=lambda item: item[0])
        candidate_limit = min(len(best_candidates), 12)
        selected_candidates = list(best_candidates[:candidate_limit])
        if is_random:
            random.shuffle(selected_candidates)
        for score, day_order, period in selected_candidates:
            key = (day_order, period)
            used_slots.add(key)
            faculty_key = (day_order, period, best_task['faculty_id'])
            faculty_busy.add(faculty_key)
            entry = {'task_id': best_task['task_id'], 'workload_id': best_task['workload_id'], 'day_order': day_order, 'period': period, 'class_id': class_id, 'subject_id': best_task['subject_id'], 'faculty_id': best_task['faculty_id']}
            class_schedule.append(entry)
            next_tasks = [task for task in tasks_left if task['task_id'] != best_task['task_id']]
            if backtrack(next_tasks):
                return True
            class_schedule.pop()
            faculty_busy.discard(faculty_key)
            used_slots.discard(key)
        return False
    success = backtrack(remaining_tasks)
    if not success:
        return None
    return class_schedule

def _generate_once(tasks, class_info, free_days, mode='efficient'):
    tasks_by_class = _group_tasks_by_class(tasks)
    faculty_total = {}
    for task in tasks:
        faculty_id = task['faculty_id']
        faculty_total[faculty_id] = faculty_total.get(faculty_id, 0) + 1
    class_priority = {}
    for class_id, class_tasks in tasks_by_class.items():
        score = 0
        faculty_counts = {}
        for task in class_tasks:
            faculty_id = task['faculty_id']
            faculty_counts[faculty_id] = faculty_counts.get(faculty_id, 0) + 1
        for faculty_id, count in faculty_counts.items():
            score += count * faculty_total.get(faculty_id, 0)
        for task in class_tasks:
            if str(task['priority']).strip().lower() == 'important':
                score += 10
        class_priority[class_id] = score
    class_ids = list(tasks_by_class.keys())
    if mode == 'random':
        random.shuffle(class_ids)
    else:
        class_ids.sort(key=lambda cid: (class_priority.get(cid, 0), -cid), reverse=True)
    faculty_busy = set()
    all_entries = []
    for class_id in class_ids:
        result = _schedule_class(class_id, tasks_by_class[class_id], free_days[class_id], faculty_busy, mode=mode)
        if result is None:
            return None
        all_entries.extend(result)
    timetable = {}
    for entry in all_entries:
        key = (entry['day_order'], entry['period'], entry['class_id'])
        timetable[key] = entry
    return timetable

def _validate_schedule(timetable, class_info, free_days):
    for class_id in class_info:
        entries = [data for data in timetable.values() if data['class_id'] == class_id]
        if len(entries) != REQUIRED_TEACHING_PERIODS:
            return False
        expected_slots = set(_get_class_teaching_slots(free_days[class_id]))
        actual_slots = {(data['day_order'], data['period']) for data in entries}
        if actual_slots != expected_slots:
            return False
        free_slot = (free_days[class_id], FREE_PERIOD)
        if free_slot in actual_slots:
            return False
    faculty_slots = set()
    for data in timetable.values():
        key = (data['day_order'], data['period'], data['faculty_id'])
        if key in faculty_slots:
            return False
        faculty_slots.add(key)
    class_slots = set()
    for data in timetable.values():
        key = (data['day_order'], data['period'], data['class_id'])
        if key in class_slots:
            return False
        class_slots.add(key)
    free_days_by_year = {}
    for class_id, info in class_info.items():
        year_group = info['year_group']
        free_day = free_days[class_id]
        free_days_by_year.setdefault(year_group, set())
        if free_day in free_days_by_year[year_group]:
            return False
        free_days_by_year[year_group].add(free_day)
    return True

def _save_timetable(timetable, target_class_id=None):
    create_timetable_table()
    conn = get_connection()
    try:
        if target_class_id is not None:
            conn.execute('DELETE FROM timetable WHERE class_id = ?', (target_class_id,))
        else:
            conn.execute('DELETE FROM timetable')
        for data in timetable.values():
            conn.execute('\n                INSERT INTO timetable\n                (\n                    day_order,\n                    period,\n                    class_id,\n                    subject_id,\n                    faculty_id\n                )\n                VALUES (?, ?, ?, ?, ?)\n                ', (data['day_order'], data['period'], data['class_id'], data['subject_id'], data['faculty_id']))
        conn.commit()
    except sqlite3.Error as error:
        conn.rollback()
        raise ValueError(f'Unable to save timetable:\n{error}')
    finally:
        conn.close()

def generate_timetable(max_attempts=300, target_class_id=None, mode='efficient'):
    if target_class_id is not None:
        return generate_timetable_for_class(target_class_id, max_attempts=max_attempts, mode=mode)
    '\n    Main timetable generation function.\n\n    FINAL RULE:\n\n        Each class:\n            29 teaching periods\n            1 FREE period\n\n        FREE:\n            Period 5 only\n\n        Same year:\n            FREE Day Order must be unique\n\n        Different classes:\n            SAME Day Order + Period is allowed\n\n        Faculty:\n            SAME Day Order + Period is NOT allowed\n    '
    create_workload_table()
    create_timetable_table()
    raw_workloads = _get_workloads()
    if not raw_workloads:
        raise ValueError('No faculty workload found.\n\nPlease add Faculty Workload first.')
    workloads = []
    class_info = {}
    for row in raw_workloads:
        workload_id, faculty_id, class_id, subject_id, priority, periods_per_week, faculty_name, class_name, department, semester, academic_year, subject_code, subject_name = row
        periods_per_week = int(periods_per_week)
        if periods_per_week <= 0:
            raise ValueError(f'Invalid periods/week:\n{subject_name}\n{class_name}')
        workload = {'workload_id': workload_id, 'faculty_id': faculty_id, 'class_id': class_id, 'subject_id': subject_id, 'priority': priority, 'periods_per_week': periods_per_week, 'faculty_name': faculty_name, 'class_name': class_name, 'department': department, 'semester': semester, 'academic_year': academic_year, 'subject_code': subject_code, 'subject_name': subject_name}
        workloads.append(workload)
        if class_id not in class_info:
            class_info[class_id] = {'class_name': class_name, 'department': department, 'semester': semester, 'academic_year': academic_year, 'year_group': _get_year_group(class_name, academic_year)}
    class_totals = {}
    for workload in workloads:
        class_id = workload['class_id']
        class_totals[class_id] = class_totals.get(class_id, 0) + workload['periods_per_week']
    invalid_classes = []
    for class_id, info in class_info.items():
        total = class_totals.get(class_id, 0)
        if total != REQUIRED_TEACHING_PERIODS:
            invalid_classes.append((info['class_name'], total))
    if invalid_classes:
        details = '\n'.join([f'• {class_name}: {total} periods assigned' for class_name, total in invalid_classes])
        raise ValueError(f'Every class must have exactly {REQUIRED_TEACHING_PERIODS} assigned teaching periods.\n\nCurrent class-wise workload:\n{details}\n\nIMPORTANT:\nThe total of all classes can be greater than 29. That is completely valid.\n\nExample:\nBCA = 29\nBCOM = 29\nTotal = 58')
    try:
        tasks = _build_tasks(workloads, class_info)
    except ValueError:
        raise
    faculty_totals = {}
    faculty_names = {}
    for task in tasks:
        faculty_id = task['faculty_id']
        faculty_totals[faculty_id] = faculty_totals.get(faculty_id, 0) + 1
        faculty_names[faculty_id] = task['faculty_name']
    overloaded = []
    for faculty_id, total in faculty_totals.items():
        if total > TOTAL_SLOTS_PER_CLASS:
            overloaded.append(f'• {faculty_names[faculty_id]}: {total} periods')
    if overloaded:
        raise ValueError('Faculty workload conflict detected.\n\nThe following faculty members have more than 30 assigned periods:\n\n' + '\n'.join(overloaded))
    classes_by_year = {}
    for class_id, info in class_info.items():
        year_group = info['year_group']
        classes_by_year.setdefault(year_group, []).append(class_id)
    for year_group, class_ids in classes_by_year.items():
        if len(class_ids) > DAY_ORDERS:
            names = [class_info[cid]['class_name'] for cid in class_ids]
            raise ValueError(f"Year group '{year_group}' has {len(class_ids)} classes.\n\nClasses:\n" + '\n'.join((f'• {name}' for name in names)) + f'\n\nOnly {DAY_ORDERS} Day Orders are available for unique FREE periods.')
    for attempt in range(1, max_attempts + 1):
        free_days = _assign_free_days(class_info, randomized=mode == 'random')
        if free_days is None:
            continue
        timetable = _generate_once(tasks, class_info, free_days, mode=mode)
        if timetable is None:
            continue
        if not _validate_schedule(timetable, class_info, free_days):
            continue
        _save_timetable(timetable)
        return True
    raise ValueError(f'Unable to generate the timetable after {max_attempts} attempts.\n\nThe class-wise workload totals are valid, but the faculty assignments could not be placed without a faculty clash.\n\nRules checked:\n• 29 teaching periods per class\n• 1 FREE period per class\n• FREE is Period 5\n• Same-year classes have different FREE Day Orders\n• Different classes may share the same Day/Period\n• Same faculty cannot teach two classes at once\n• Same class cannot have two subjects at once')

def get_all_timetable():
    create_timetable_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                t.id,\n                t.day_order,\n                t.period,\n\n                t.class_id,\n                c.class_name,\n\n                t.subject_id,\n                s.subject_code,\n                s.subject_name,\n\n                t.faculty_id,\n                f.name AS faculty_name\n\n            FROM timetable t\n\n            INNER JOIN classes c\n                ON t.class_id = c.id\n\n            INNER JOIN subjects s\n                ON t.subject_id = s.id\n\n            INNER JOIN faculty f\n                ON t.faculty_id = f.id\n\n            ORDER BY\n                t.class_id,\n                t.day_order,\n                t.period\n            ')
        return cursor.fetchall()
    finally:
        conn.close()

def get_timetable_by_class(class_id):
    create_timetable_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                t.day_order,\n                t.period,\n\n                c.class_name,\n\n                s.subject_code,\n                s.subject_name,\n\n                f.name AS faculty_name,\n                c.semester AS class_semester,\n                s.semester AS subject_semester\n\n            FROM timetable t\n\n            INNER JOIN classes c\n                ON t.class_id = c.id\n\n            INNER JOIN subjects s\n                ON t.subject_id = s.id\n\n            INNER JOIN faculty f\n                ON t.faculty_id = f.id\n\n            WHERE t.class_id = ?\n\n            ORDER BY\n                t.day_order,\n                t.period\n            ', (class_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_timetable_by_faculty(faculty_id):
    create_timetable_table()
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT\n                t.day_order,\n                t.period,\n\n                f.name AS faculty_name,\n\n                c.class_name,\n\n                s.subject_code,\n                s.subject_name,\n                c.semester AS class_semester,\n                s.semester AS subject_semester\n\n            FROM timetable t\n\n            INNER JOIN classes c\n                ON t.class_id = c.id\n\n            INNER JOIN subjects s\n                ON t.subject_id = s.id\n\n            INNER JOIN faculty f\n                ON t.faculty_id = f.id\n\n            WHERE t.faculty_id = ?\n\n            ORDER BY\n                t.day_order,\n                t.period\n            ', (faculty_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def clear_timetable():
    create_timetable_table()
    conn = get_connection()
    try:
        conn.execute('DELETE FROM timetable')
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()
create_timetable_table()

def generate_timetable_for_class(target_class_id, max_attempts=300, mode='efficient'):
    create_workload_table()
    create_timetable_table()
    raw_workloads = _get_workloads(target_class_id=target_class_id)
    if not raw_workloads:
        raise ValueError('No faculty workload found for the selected class.\n\nPlease assign faculty workload for this class first.')
    workloads = []
    class_info = {}
    for row in raw_workloads:
        workload_id, faculty_id, class_id, subject_id, priority, periods_per_week, faculty_name, class_name, department, semester, academic_year, subject_code, subject_name = row
        periods_per_week = int(periods_per_week)
        if periods_per_week <= 0:
            raise ValueError(f'Invalid periods/week for subject {subject_name}')
        workload = {'workload_id': workload_id, 'faculty_id': faculty_id, 'class_id': class_id, 'subject_id': subject_id, 'priority': priority, 'periods_per_week': periods_per_week, 'faculty_name': faculty_name, 'class_name': class_name, 'department': department, 'semester': semester, 'academic_year': academic_year, 'subject_code': subject_code, 'subject_name': subject_name}
        workloads.append(workload)
        if class_id not in class_info:
            class_info[class_id] = {'class_name': class_name, 'department': department, 'semester': semester, 'academic_year': academic_year, 'year_group': _get_year_group(class_name, academic_year)}
    total_periods = sum((w['periods_per_week'] for w in workloads))
    if total_periods != REQUIRED_TEACHING_PERIODS:
        cname = class_info[target_class_id]['class_name']
        raise ValueError(f"The selected class '{cname}' has {total_periods} periods assigned.\n\nIt must have exactly {REQUIRED_TEACHING_PERIODS} teaching periods to generate a valid timetable.")
    tasks = _build_tasks(workloads, class_info)
    conn = get_connection()
    try:
        cursor = conn.execute('\n            SELECT t.day_order, t.period, t.faculty_id, t.class_id, c.class_name, c.academic_year\n            FROM timetable t\n            INNER JOIN classes c ON t.class_id = c.id\n            WHERE t.class_id != ?\n            ', (target_class_id,))
        existing_rows = cursor.fetchall()
    finally:
        conn.close()
    existing_faculty_busy = {(r[0], r[1], r[2]) for r in existing_rows}
    target_year = class_info[target_class_id]['year_group']
    used_same_year_free_days = set()
    other_classes_slots = {}
    for r in existing_rows:
        day_o, per, fac, cid, cname, ac_yr = r
        other_classes_slots.setdefault(cid, {'year_group': _get_year_group(cname, ac_yr), 'p5_days': set()})
        if per == FREE_PERIOD:
            other_classes_slots[cid]['p5_days'].add(day_o)
    for cid, cdata in other_classes_slots.items():
        if cdata['year_group'] == target_year:
            missing_p5 = set(range(1, DAY_ORDERS + 1)) - cdata['p5_days']
            if missing_p5:
                used_same_year_free_days.add(next(iter(missing_p5)))
    available_free_days = [d for d in range(1, DAY_ORDERS + 1) if d not in used_same_year_free_days]
    if not available_free_days:
        available_free_days = list(range(1, DAY_ORDERS + 1))
    if mode == 'random':
        available_free_days = list(available_free_days)
        random.shuffle(available_free_days)
    for attempt in range(1, max_attempts + 1):
        free_day = available_free_days[attempt % len(available_free_days)]
        faculty_busy = set(existing_faculty_busy)
        class_result = _schedule_class(target_class_id, tasks, free_day, faculty_busy, mode=mode)
        if class_result is None:
            continue
        timetable_dict = {}
        for entry in class_result:
            key = (entry['day_order'], entry['period'], entry['class_id'])
            timetable_dict[key] = entry
        _save_timetable(timetable_dict, target_class_id=target_class_id)
        return True
    cname = class_info[target_class_id]['class_name']
    raise ValueError(f"Unable to generate schedule for '{cname}' without faculty conflicts against existing classes after {max_attempts} attempts.\n\nPlease check faculty assignments or adjust workload.")
