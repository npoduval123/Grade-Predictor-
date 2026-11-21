import sqlite3

DB_NAME = "grades.db"


def get_classes():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM classes ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_categories(class_id):
    """Returns (category_id, name, weight, score) for each category.
    score is None if no score has been entered yet."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT categories.id, categories.name, categories.weight, scores.score
        FROM categories
        LEFT JOIN scores ON scores.category_id = categories.id
        WHERE categories.class_id = ?
        ORDER BY categories.id
    """, (class_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def save_score(category_id, score):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO scores (category_id, score) VALUES (?, ?)",
        (category_id, score),
    )
    conn.commit()
    conn.close()


def points_so_far(class_id):
    """Returns (points earned, total weight that has a score)."""
    earned = 0
    graded_weight = 0
    for cat_id, name, weight, score in get_categories(class_id):
        if score is not None:
            earned += weight * score / 100
            graded_weight += weight
    return earned, graded_weight


def current_grade(class_id):
    earned, graded_weight = points_so_far(class_id)
    if graded_weight == 0:
        return None
    return round(earned / graded_weight * 100, 2)


def clear_scores(class_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM scores
        WHERE category_id IN (SELECT id FROM categories WHERE class_id = ?)
    """, (class_id,))
    conn.commit()
    conn.close()


def score_needed(class_id, target):
    """Average score needed on the remaining work to finish at the target grade.
    With no scores entered this is mode 1; with some scores it is mode 2."""
    earned, graded_weight = points_so_far(class_id)
    remaining_weight = 100 - graded_weight
    if remaining_weight <= 0:
        return None
    return round((target - earned) / remaining_weight * 100, 2)


def points_you_can_lose(class_id, target):
    """How many more points you can lose and still finish at the target.
    A negative number means the target is already out of reach."""
    earned, graded_weight = points_so_far(class_id)
    lost_so_far = graded_weight - earned
    return round((100 - target) - lost_so_far, 2)


def what_if_table(class_id, target, category_id, test_scores=(100, 90, 80, 70, 60, 0)):
    """For one category with no score yet, returns (test score, average needed
    on everything else) for each test score."""
    earned, graded_weight = points_so_far(class_id)
    weight = None
    for cat_id, name, w, score in get_categories(class_id):
        if cat_id == category_id:
            if score is not None:
                return None
            weight = w
    if weight is None:
        return None

    remaining_weight = 100 - graded_weight - weight
    rows = []
    for s in test_scores:
        new_earned = earned + weight * s / 100
        if remaining_weight <= 0:
            needed = None
        else:
            needed = round((target - new_earned) / remaining_weight * 100, 2)
        rows.append((s, needed))
    return rows


