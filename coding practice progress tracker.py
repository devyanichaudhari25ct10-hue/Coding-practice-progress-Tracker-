import tkinter as tk
from tkinter import ttk
import mysql.connector


# ---------------- MYSQL CONNECTION ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dikshu@18",
    database="coding_tracker"
)

cursor = db.cursor()


# ---------------- LOGIN WINDOW ----------------

root = tk.Tk()
root.title("Coding Practice Progress Tracker")
root.geometry("500x400")


tk.Label(root, text="CODING PRACTICE TRACKER",
         font=("Arial", 18, "bold")).pack(pady=30)

tk.Label(root, text="Username").pack()
username_entry = tk.Entry(root)
username_entry.pack(pady=5)

tk.Label(root, text="Password").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

login_message = tk.Label(root, text="")
login_message.pack(pady=10)


def login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )

    result = cursor.fetchone()

    if result:
        root.destroy()
        open_dashboard()
    else:
        login_message.config(text="Invalid username or password")


tk.Button(root, text="Login",
          command=login,
          width=15).pack(pady=10)


# ---------------- DASHBOARD ----------------

def open_dashboard():

    dash = tk.Tk()
    dash.title("Coding Practice Dashboard")
    dash.geometry("1000x650")

    tk.Label(
        dash,
        text="CODING PRACTICE PROGRESS TRACKER",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # -------- FORM --------

    form = tk.Frame(dash)
    form.pack(pady=10)

    tk.Label(form, text="Problem Name").grid(row=0, column=0, padx=5, pady=5)
    problem_entry = tk.Entry(form, width=25)
    problem_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form, text="Topic").grid(row=0, column=2, padx=5, pady=5)
    topic_entry = tk.Entry(form, width=20)
    topic_entry.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(form, text="Language").grid(row=1, column=0, padx=5, pady=5)

    language_box = ttk.Combobox(
        form,
        values=["C", "C++", "Python", "Java"],
        width=18
    )
    language_box.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(form, text="Difficulty").grid(row=1, column=2, padx=5, pady=5)

    difficulty_box = ttk.Combobox(
        form,
        values=["Easy", "Medium", "Hard"],
        width=18
    )
    difficulty_box.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(form, text="Status").grid(row=2, column=0, padx=5, pady=5)

    status_box = ttk.Combobox(
        form,
        values=["Solved", "Unsolved"],
        width=18
    )
    status_box.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(form, text="Practice Date").grid(row=2, column=2, padx=5, pady=5)

    date_entry = tk.Entry(form, width=20)
    date_entry.grid(row=2, column=3, padx=5, pady=5)


    # -------- TREEVIEW --------

    columns = (
        "ID",
        "Problem",
        "Topic",
        "Language",
        "Difficulty",
        "Status",
        "Date"
    )

    table = ttk.Treeview(
        dash,
        columns=columns,
        show="headings",
        height=12
    )

    for col in columns:
        table.heading(col, text=col)

    table.column("ID", width=40)
    table.column("Problem", width=180)
    table.column("Topic", width=100)
    table.column("Language", width=80)
    table.column("Difficulty", width=90)
    table.column("Status", width=80)
    table.column("Date", width=100)

    table.pack(pady=15)


    # -------- FUNCTIONS --------

    def clear_fields():
        problem_entry.delete(0, tk.END)
        topic_entry.delete(0, tk.END)
        language_box.set("")
        difficulty_box.set("")
        status_box.set("")
        date_entry.delete(0, tk.END)


    def show_records():

        for item in table.get_children():
            table.delete(item)

        cursor.execute("SELECT * FROM problems")
        records = cursor.fetchall()

        for record in records:
            table.insert("", tk.END, values=record)


    def add_problem():

        problem = problem_entry.get()
        topic = topic_entry.get()
        language = language_box.get()
        difficulty = difficulty_box.get()
        status = status_box.get()
        date = date_entry.get()

        if problem == "" or topic == "":
            return

        cursor.execute(
            """
            INSERT INTO problems
            (problem_name, topic, language, difficulty, status, practice_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (problem, topic, language, difficulty, status, date)
        )

        db.commit()

        clear_fields()
        show_records()
        update_progress()


    def delete_problem():

        selected = table.selection()

        if selected:
            values = table.item(selected[0])["values"]
            problem_id = values[0]

            cursor.execute(
                "DELETE FROM problems WHERE id=%s",
                (problem_id,)
            )

            db.commit()

            show_records()
            update_progress()


    def select_record(event):

        selected = table.selection()

        if selected:

            values = table.item(selected[0])["values"]

            problem_entry.delete(0, tk.END)
            problem_entry.insert(0, values[1])

            topic_entry.delete(0, tk.END)
            topic_entry.insert(0, values[2])

            language_box.set(values[3])
            difficulty_box.set(values[4])
            status_box.set(values[5])

            date_entry.delete(0, tk.END)
            date_entry.insert(0, values[6])


    def update_problem():

        selected = table.selection()

        if selected:

            values = table.item(selected[0])["values"]
            problem_id = values[0]

            cursor.execute(
                """
                UPDATE problems
                SET problem_name=%s,
                    topic=%s,
                    language=%s,
                    difficulty=%s,
                    status=%s,
                    practice_date=%s
                WHERE id=%s
                """,
                (
                    problem_entry.get(),
                    topic_entry.get(),
                    language_box.get(),
                    difficulty_box.get(),
                    status_box.get(),
                    date_entry.get(),
                    problem_id
                )
            )

            db.commit()

            clear_fields()
            show_records()
            update_progress()


    def search_problem():

        search = search_entry.get()

        for item in table.get_children():
            table.delete(item)

        cursor.execute(
            """
            SELECT * FROM problems
            WHERE problem_name LIKE %s
            OR topic LIKE %s
            """,
            ("%" + search + "%", "%" + search + "%")
        )

        records = cursor.fetchall()

        for record in records:
            table.insert("", tk.END, values=record)


    # -------- BUTTONS --------

    button_frame = tk.Frame(dash)
    button_frame.pack(pady=5)

    tk.Button(
        button_frame,
        text="Add Problem",
        command=add_problem,
        width=15
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        button_frame,
        text="Update",
        command=update_problem,
        width=15
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        button_frame,
        text="Delete",
        command=delete_problem,
        width=15
    ).grid(row=0, column=2, padx=5)

    tk.Button(
        button_frame,
        text="Clear",
        command=clear_fields,
        width=15
    ).grid(row=0, column=3, padx=5)


    # -------- SEARCH --------

    search_frame = tk.Frame(dash)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search").pack(side=tk.LEFT)

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side=tk.LEFT, padx=5)

    tk.Button(
        search_frame,
        text="Search",
        command=search_problem
    ).pack(side=tk.LEFT)

    tk.Button(
        search_frame,
        text="Show All",
        command=show_records
    ).pack(side=tk.LEFT, padx=5)


    # -------- PROGRESS --------

    progress_label = tk.Label(
        dash,
        text="",
        font=("Arial", 13, "bold")
    )

    progress_label.pack(pady=10)


    def update_progress():

        cursor.execute("SELECT COUNT(*) FROM problems")
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM problems WHERE status='Solved'"
        )
        solved = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM problems WHERE status='Unsolved'"
        )
        unsolved = cursor.fetchone()[0]

        progress_label.config(
            text="Total: " + str(total) +
                 "     Solved: " + str(solved) +
                 "     Unsolved: " + str(unsolved)
        )


    table.bind("<ButtonRelease-1>", select_record)

    show_records()
    update_progress()

    dash.mainloop()


root.mainloop()
