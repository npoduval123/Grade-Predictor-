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