
import pandas as pd
from collections import defaultdict
import random

def generate_timetables(uploaded_file):
    excel_data = pd.ExcelFile(uploaded_file)
    unified_df = excel_data.parse('Unified Timetable')
    data_df = excel_data.parse('Data')

    days = unified_df['DAY'].unique()
    periods = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9']
    schedule = defaultdict(lambda: defaultdict(dict))
    teacher_schedule = defaultdict(lambda: defaultdict(list))
    teacher_load = defaultdict(int)
    assignments = data_df.copy()
    assignments['Teacher'] = assignments['Teacher'].str.strip().str.upper()
    assignments['Assigned'] = 0

    def can_assign_teacher(teacher, day, period):
        assigned_periods = teacher_schedule[teacher][day]
        period_index = int(period[1:])
        if period_index in assigned_periods:
            return False
        if (period_index - 1 in assigned_periods and period_index - 2 in assigned_periods) or            (period_index + 1 in assigned_periods and period_index + 2 in assigned_periods):
            return False
        return True

    for _, row in assignments.iterrows():
        cls, subject, teacher, count = row['Class'], row['Subject'], row['Teacher'], int(row['Target Count'])
        remaining = count
        while remaining > 0:
            random_days = list(days)
            random.shuffle(random_days)
            for day in random_days:
                for period in periods:
                    if period == 'P6': continue
                    if period in schedule[cls][day]: continue
                    if not can_assign_teacher(teacher, day, period): continue
                    schedule[cls][day][period] = (subject, teacher)
                    teacher_schedule[teacher][day].append(int(period[1:]))
                    teacher_load[teacher] += 1
                    remaining -= 1
                    if remaining == 0:
                        break
                if remaining == 0:
                    break

    filled_unified = unified_df.copy()
    for idx, row in filled_unified.iterrows():
        day, cls = row['DAY'], row['TIME / CLASS']
        for period in periods:
            if period == 'P6':
                filled_unified.at[idx, period] = "LONG BREAK"
            elif period in schedule[cls][day]:
                subj, teacher = schedule[cls][day][period]
                filled_unified.at[idx, period] = f"{subj}\n{teacher}"

    class_timetables = defaultdict(lambda: pd.DataFrame(index=days, columns=periods[:-1]))
    for cls in schedule:
        for day in days:
            for period in periods[:-1]:
                if period == 'P6':
                    class_timetables[cls].loc[day, period] = "LONG BREAK"
                elif period in schedule[cls][day]:
                    subject, teacher = schedule[cls][day][period]
                    class_timetables[cls].loc[day, period] = f"{subject}\n{teacher}"
                else:
                    class_timetables[cls].loc[day, period] = ""

    teacher_timetables = defaultdict(lambda: pd.DataFrame(index=days, columns=periods[:-1]))
    for cls in schedule:
        for day in schedule[cls]:
            for period in schedule[cls][day]:
                if period == 'P6': continue
                subject, teacher = schedule[cls][day][period]
                entry = f"{subject}\n{cls}"
                teacher_timetables[teacher].loc[day, period] = entry

    for tt in teacher_timetables.values():
        for day in days:
            for period in periods[:-1]:
                if pd.isna(tt.loc[day, period]):
                    tt.loc[day, period] = "LONG BREAK" if period == 'P6' else ""

    return filled_unified, class_timetables, teacher_timetables
