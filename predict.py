from grades import (get_classes, get_categories, save_score,
                    clear_scores, current_grade, score_needed,
                    points_you_can_lose, what_if_table)


def choose_class():
    classes = get_classes()
    if not classes:
        print("No classes yet. Run classes.py first.")
        return None
    print("\nClasses:")
    for i, (class_id, name) in enumerate(classes, start=1):
        print(f"{i}. {name}")
    choice = input("Pick a class number: ")
    if not choice.isdigit() or not 1 <= int(choice) <= len(classes):
        print("Please enter a number from the list.")
        return None
    return classes[int(choice) - 1]


def enter_scores(class_id):
    print("Enter your score (0-100) for each category, or press Enter to skip.")
    for cat_id, name, weight, score in get_categories(class_id):
        text = input(f"{name} ({weight}%): ")
        if text == "":
            continue
        try:
            value = float(text)
        except ValueError:
            print("  Not a number, skipped.")
            continue
        if 0 <= value <= 100:
            save_score(cat_id, value)
        else:
            print("  Must be between 0 and 100, skipped.")


def show_result(class_id):
    text = input("Target grade for this class (like 90): ")
    try:
        target = float(text)
    except ValueError:
        print("Please enter a number.")
        return
    needed = score_needed(class_id, target)
    if needed is None:
        print("Every category already has a score, so nothing is left to earn.")
    elif needed <= 0:
        print("You have already secured that grade.")
    elif needed > 100:
        print(f"You would need {needed}% on the rest, which is out of reach.")
    else:
        print(f"You need an average of {needed}% on the remaining work.")


def explore(class_id):
    text = input("Target grade for this class (like 90): ")
    try:
        target = float(text)
    except ValueError:
        print("Please enter a number.")
        return

    cushion = points_you_can_lose(class_id, target)
    if cushion < 0:
        print("That target is out of reach.")
        return
    print(f"\nTo finish with {target}%, you can lose up to {cushion} points in total.")
    print("A category worth 5% can cost you at most 5 of those points.\n")

    cats = get_categories(class_id)
    print("Which category do you want to test?")
    for i, (cat_id, name, weight, score) in enumerate(cats, start=1):
        print(f"{i}. {name} ({weight}%)")
    choice = input("Pick a number: ")
    if not choice.isdigit() or not 1 <= int(choice) <= len(cats):
        print("Please enter a number from the list.")
        return

    cat_id, name, weight, score = cats[int(choice) - 1]
    print(f"\nIf you score this on {name}, you need this average on everything else:")
    for s, needed in what_if_table(class_id, target, cat_id):
        if needed is None:
            print(f"  {s}% on {name}: nothing else is left to earn")
        elif needed > 100:
            print(f"  {s}% on {name}: out of reach ({needed}%)")
        elif needed <= 0:
            print(f"  {s}% on {name}: you would already be safe")
        else:
            print(f"  {s}% on {name}: {needed}% on the rest")


def main():
    picked = choose_class()
    if picked is None:
        return
    class_id, class_name = picked
    print(f"\n{class_name}")
    print("1. I have no scores yet")
    print("2. I want to enter the scores I have")
    mode = input("Pick 1 or 2: ")
    if mode == "1":
        clear_scores(class_id)
        explore(class_id)
    elif mode == "2":
        clear_scores(class_id)
        enter_scores(class_id)
        grade = current_grade(class_id)
        if grade is not None:
            print(f"Your grade so far: {grade}%")
        show_result(class_id)
    else:
        print("Please pick 1 or 2.")


if __name__ == "__main__":
    main()