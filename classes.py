import sqlite3

DB_NAME = "grades.db"


def add_class(class_name, categories):
    """categories is a list of (category_name, weight) pairs.
    Returns (True or False, a message the caller can show)."""
    total = sum(weight for name, weight in categories)
    # 0.01 tolerance because decimals like 33.3 are stored slightly imprecisely.
    if abs(total - 100) > 0.01:
        return False, f"Weights add up to {total:g}%, but they must add up to exactly 100%."

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO classes (name) VALUES (?)", (class_name,))
        class_id = cur.lastrowid
        for cat_name, weight in categories:
            cur.execute(
                "INSERT INTO categories (class_id, name, weight) VALUES (?, ?, ?)",
                (class_id, cat_name, weight),
            )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return False, f"{class_name} already exists."
    finally:
        conn.close()

    return True, f"Saved {class_name}."


STARTER_CLASSES = [
    ("CS 180", [
        ("Homework", 10), ("Projects", 30),
        ("Midterm 1", 15), ("Midterm 2", 15),
        ("Midterm 3", 15), ("Midterm 4", 15)]),
    ("MA 161", [
        ("Quizzes", 15), ("Homework", 10), ("Midterm 1", 20),
        ("Midterm 2", 20), ("Final", 35)]),
    ("SCLA 101", [
        ("Essays", 50), ("Participation", 10), ("Final", 40)]),
    ("CHEM 217", [
        ("Exam 1", 20), ("Exam 2", 20), ("Exam 3", 20),
        ("Homework", 15), ("Final", 25)]),
]

if __name__ == "__main__":
    for class_name, categories in STARTER_CLASSES:
        ok, message = add_class(class_name, categories)
        print(message)