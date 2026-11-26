from flask import Flask, render_template, request, redirect, url_for, session

from grades import (get_classes, get_categories, save_score, clear_scores,
                    current_grade, score_needed, points_you_can_lose,
                    what_if_table, parse_target, describe_needed,
                    needed_for_each_letter)

app = Flask(__name__)
app.secret_key = "change-this-later"


def logged_in():
    return bool(session.get("name"))


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["name"] = request.form["name"].strip()
        return redirect(url_for("menu"))
    return render_template("home.html")


@app.route("/menu")
def menu():
    if not logged_in():
        return redirect(url_for("home"))
    return render_template("menu.html", name=session["name"])


@app.route("/classes", methods=["GET", "POST"])
def choose_class():
    if not logged_in():
        return redirect(url_for("home"))
    if request.method == "POST":
        class_id = int(request.form["class_id"])
        return redirect(url_for("class_home", class_id=class_id))
    return render_template("classes.html", classes=get_classes())


@app.route("/class/<int:class_id>")
def class_home(class_id):
    if not logged_in():
        return redirect(url_for("home"))
    class_name = dict(get_classes()).get(class_id)
    if class_name is None:
        return redirect(url_for("choose_class"))
    return render_template("class_home.html", class_id=class_id,
                           class_name=class_name)


@app.route("/class/<int:class_id>/plan", methods=["GET", "POST"])
def plan(class_id):
    """Mode 1: no scores yet. Shows the what-if table."""
    if not logged_in():
        return redirect(url_for("home"))
    class_name = dict(get_classes()).get(class_id)
    if class_name is None:
        return redirect(url_for("choose_class"))

    categories = get_categories(class_id)
    error = None
    result = None

    if request.method == "POST":
        target = parse_target(request.form["target"])
        if target is None:
            error = "Please enter a number like 90, or a letter like B."
        else:
            clear_scores(class_id)
            cushion = points_you_can_lose(class_id, target)
            if cushion < 0:
                error = "That target is out of reach."
            else:
                cat_id = int(request.form["category_id"])
                cat_name = ""
                for c_id, name, weight, score in categories:
                    if c_id == cat_id:
                        cat_name = name
                rows = [(s, describe_needed(needed))
                        for s, needed in what_if_table(class_id, target, cat_id)]
                result = {"target": target, "cushion": cushion,
                          "category": cat_name, "rows": rows}

    return render_template("plan.html", class_id=class_id,
                           class_name=class_name, categories=categories,
                           error=error, result=result)


@app.route("/class/<int:class_id>/scores", methods=["GET", "POST"])
def scores(class_id):
    """Mode 2: some scores entered. Shows what is needed on the rest."""
    if not logged_in():
        return redirect(url_for("home"))
    class_name = dict(get_classes()).get(class_id)
    if class_name is None:
        return redirect(url_for("choose_class"))

    categories = get_categories(class_id)
    error = None
    result = None

    if request.method == "POST":
        target = parse_target(request.form["target"])
        if target is None:
            error = "Please enter a number like 90, or a letter like B."

        entered = {}
        if error is None:
            for cat_id, name, weight, score in categories:
                text = request.form.get(f"score_{cat_id}", "").strip()
                if text == "":
                    continue
                try:
                    value = float(text)
                except ValueError:
                    error = f"{name}: please enter a number."
                    break
                if not 0 <= value <= 100:
                    error = f"{name}: score must be between 0 and 100."
                    break
                entered[cat_id] = value

        if error is None:
            clear_scores(class_id)
            for cat_id, value in entered.items():
                save_score(cat_id, value)
            letters = [(letter, cutoff, describe_needed(needed))
                       for letter, cutoff, needed in needed_for_each_letter(class_id)]
            result = {"grade": current_grade(class_id),
                      "target": target,
                      "message": describe_needed(score_needed(class_id, target)),
                      "letters": letters}

    return render_template("scores.html", class_id=class_id,
                           class_name=class_name, categories=categories,
                           error=error, result=result)


if __name__ == "__main__":
    app.run(debug=True)