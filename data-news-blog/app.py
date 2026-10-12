import os
from functools import wraps
from flask import Flask, render_template, abort, request, redirect, url_for, session, flash
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    search_q = request.args.get("q", "").strip()

    query = supabase.table("posts").select("*").order("created_at", desc=True)

    if search_q:
        query = query.or_(f"title.ilike.%{search_q}%,content.ilike.%{search_q}%")

    response = query.execute()
    posts = response.data
    return render_template("index.html", posts=posts)


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    response = (
        supabase.table("posts")
        .select("*")
        .eq("id", post_id)
        .execute()
    )
    if not response.data:
        abort(404)
    post = response.data[0]
    return render_template("post.html", post=post)


@app.route("/category/<category_name>")
def category(category_name):
    response = (
        supabase.table("posts")
        .select("*")
        .eq("category", category_name)
        .order("created_at", desc=True)
        .execute()
    )
    posts = response.data
    return render_template("index.html", posts=posts, active_category=category_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            result = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if result.user:
                session["user_email"] = result.user.email
                session["user_name"] = (result.user.user_metadata or {}).get("name") or result.user.email.split("@")[0]
                return redirect(url_for("add_post"))
        except Exception:
            flash("Wrong email or password.")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"name": name}},
            })
            flash("Hesab yaradildi! Indi daxil ola bilersen.")
            return redirect(url_for("login"))
        except Exception:
            flash("Qeydiyyat alinmadi, yeniden cehd et.")
            return redirect(url_for("signup"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        category_value = request.form.get("category")
        source_url = request.form.get("source_url") or None
        image_url = request.form.get("image_url") or None
        author = session.get("user_name") or session.get("user_email")

        supabase.table("posts").insert({
            "title": title,
            "content": content,
            "category": category_value,
            "source_url": source_url,
            "image_url": image_url,
            "author": author,
        }).execute()

        flash("Post published!")
        return redirect(url_for("index"))

    return render_template("add_post.html")


@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    response = (
        supabase.table("posts")
        .select("author")
        .eq("id", post_id)
        .execute()
    )
    if not response.data:
        abort(404)

    post_author = response.data[0].get("author")
    current_user = session.get("user_name") or session.get("user_email")

    if post_author != current_user:
        flash("You can only delete your own posts.")
        return redirect(url_for("post_detail", post_id=post_id))

    supabase.table("posts").delete().eq("id", post_id).execute()
    flash("Post deleted.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
