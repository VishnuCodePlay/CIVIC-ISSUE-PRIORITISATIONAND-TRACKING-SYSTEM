import mysql.connector
from mysql.connector import Error
from datetime import datetime


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456789",
    "database": "civic_issues_db"
}

CATEGORY_SCORES = {
    "Pothole": 3, "Broken Streetlight": 2, "Overflowing Garbage": 2,
    "Blocked Drain": 3, "Water Leakage": 3, "Other": 1
}
SEVERITY_SCORES = {"Low": 1, "Medium": 2, "High": 3}


def connect_db():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            issue_id INT PRIMARY KEY AUTO_INCREMENT,
            reporter_name VARCHAR(100) NOT NULL,
            location VARCHAR(200) NOT NULL,
            category VARCHAR(60) NOT NULL,
            description TEXT NOT NULL,
            severity VARCHAR(20) NOT NULL,
            priority_score INT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Open',
            reported_at DATETIME NOT NULL
        )
    """)
    connection.commit()
    cursor.close()
    return connection


def calculate_priority(category, severity):
    return CATEGORY_SCORES.get(category, 1) + SEVERITY_SCORES.get(severity, 1)


def report_issue(connection):
    print("\n--- REPORT A CIVIC ISSUE ---")
    name = input("Reporter name: ").strip()
    location = input("Location/landmark: ").strip()
    print("Categories: " + ", ".join(CATEGORY_SCORES.keys()))
    category = input("Issue category (enter as listed): ").strip().title()
    if category not in CATEGORY_SCORES:
        category = "Other"
    description = input("Short description: ").strip()
    print("Severity: Low / Medium / High")
    severity = input("Severity: ").strip().title()
    if severity not in SEVERITY_SCORES:
        severity = "Medium"
    if not name or not location or not description:
        print("Error: name, location, and description are required.")
        return

    score = calculate_priority(category, severity)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO issues
        (reporter_name, location, category, description, severity,
         priority_score, status, reported_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, location, category, description, severity, score, "Open",
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    connection.commit()
    issue_id = cursor.lastrowid
    cursor.close()
    print(f"\nIssue registered successfully. Reference ID: {issue_id}")
    print(f"Priority score: {score} | Initial status: Open")


def list_issues(connection):
    cursor = connection.cursor()
    cursor.execute("""SELECT issue_id, category, location, severity, priority_score,
                      status, reported_at FROM issues
                      ORDER BY priority_score DESC, issue_id ASC""")
    rows = cursor.fetchall()
    cursor.close()
    print("\n--- CIVIC ISSUE REGISTER ---")
    if not rows:
        print("No issues have been registered.")
        return
    print(f"{'ID':<4} {'CATEGORY':<22} {'LOCATION':<24} {'SEV.':<8} "
          f"{'SCORE':<6} {'STATUS':<13} REPORTED")
    print("-" * 103)
    for row in rows:
        issue_id, category, location, severity, score, status, reported_at = row
        reported = reported_at.strftime("%Y-%m-%d %H:%M") if hasattr(reported_at, "strftime") else str(reported_at)
        print(f"{issue_id:<4} {category[:21]:<22} {location[:23]:<24} "
              f"{severity:<8} {score:<6} {status:<13} {reported}")


def search_issues(connection):
    term = input("\nEnter location or category to search: ").strip()
    like_term = f"%{term}%"
    cursor = connection.cursor()
    cursor.execute("""SELECT issue_id, category, location, description, severity,
                      priority_score, status FROM issues
                      WHERE location LIKE %s OR category LIKE %s OR description LIKE %s
                      ORDER BY priority_score DESC""", (like_term, like_term, like_term))
    rows = cursor.fetchall()
    cursor.close()
    print("\n--- SEARCH RESULTS ---")
    if not rows:
        print("No matching issues found.")
        return
    for row in rows:
        print(f"ID: {row[0]} | {row[1]} | {row[2]}")
        print(f"Description: {row[3]}")
        print(f"Severity: {row[4]} | Priority: {row[5]} | Status: {row[6]}")
        print("-" * 55)


def update_status(connection):
    print("\n--- UPDATE ISSUE STATUS ---")
    try:
        issue_id = int(input("Issue ID: "))
    except ValueError:
        print("Invalid ID. Enter a number.")
        return
    print("Allowed statuses: Open, In Progress, Resolved")
    status = input("New status: ").strip().title()
    if status not in {"Open", "In Progress", "Resolved"}:
        print("Invalid status.")
        return
    cursor = connection.cursor()
    cursor.execute("UPDATE issues SET status = %s WHERE issue_id = %s", (status, issue_id))
    connection.commit()
    updated = cursor.rowcount
    cursor.close()
    if updated == 0:
        print("No issue found with that ID.")
    else:
        print(f"Issue {issue_id} status updated to: {status}")


def show_summary(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM issues")
    total = cursor.fetchone()[0]
    counts = {}
    for status in ("Open", "In Progress", "Resolved"):
        cursor.execute("SELECT COUNT(*) FROM issues WHERE status = %s", (status,))
        counts[status] = cursor.fetchone()[0]
    cursor.close()
    print("\n--- ISSUE SUMMARY ---")
    print(f"Total issues      : {total}")
    print(f"Open              : {counts['Open']}")
    print(f"In Progress       : {counts['In Progress']}")
    print(f"Resolved          : {counts['Resolved']}")


def main():
    try:
        connection = connect_db()
    except Error as error:
        print("Could not connect to MySQL.")
        print("Check that MySQL Server is running and DB_CONFIG is correct.")
        print(f"MySQL error: {error}")
        return
    try:
        while True:
            print("\n======================================")
            print(" CIVIC ISSUE PRIORITISATION SYSTEM")
            print("======================================")
            print("1. Report a new issue")
            print("2. View all issues")
            print("3. Search issues")
            print("4. Update issue status")
            print("5. View summary")
            print("0. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                report_issue(connection)
            elif choice == "2":
                list_issues(connection)
            elif choice == "3":
                search_issues(connection)
            elif choice == "4":
                update_status(connection)
            elif choice == "5":
                show_summary(connection)
            elif choice == "0":
                print("  \n  ======================================")
                print("          THANK YOU FOR USING \nExiting Civic Issue Prioritisation System.")
                print("  ======================================")
                break
            else:
                print("Invalid option. Please try again.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
