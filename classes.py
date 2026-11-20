import sqlite3

DB_NAME = "grades.db"


def add_class(class_name, categories):
    """categories is a list of (category_name, weight) pairs."""
    total = sum(weight for name, weight in categories)
    if abs(total - 100) > 0.01:
        print(f"Not saved: weights for {class_name} add up to {total}, not 100.")
        return False

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
        conn.close()
        print(f"Not saved: {class_name} already exists.")
        return False

    conn.close()
    print(f"Saved {class_name}.")
    return True


if __name__ == "__main__":
    add_class("CS 101 (sample)", [
        ("Homework", 20), ("Projects", 30), ("Midterm", 20), ("Final", 30)])
    add_class("MA 101 (sample)", [
        ("Quizzes", 15), ("Homework", 10), ("Midterm 1", 20),
        ("Midterm 2", 20), ("Final", 35)])
    add_class("ENG 101 (sample)", [
        ("Essays", 50), ("Participation", 10), ("Final", 40)])
    # This one is on purpose: the weights add up to 80, so it should be rejected.
    add_class("Bad Weights (test)", [("Homework", 50), ("Final", 30)])