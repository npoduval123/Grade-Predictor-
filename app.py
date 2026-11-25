from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "change-this-later"


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        session["name"] = request.form["name"].strip()
        return redirect(url_for("menu"))
    return render_template("home.html")


@app.route("/menu")
def menu():
    name = session.get("name")
    if not name:
        return redirect(url_for("home"))
    return render_template("menu.html", name=name)


if __name__ == "__main__":
    app.run(debug=True)