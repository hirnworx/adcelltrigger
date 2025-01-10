import asyncio
import time
import mysql.connector
from mysql.connector import Error
from pyppeteer import launch

# MySQL-Konfiguration
DB_CONFIG = {
    'host': '202.61.192.15',        # Hostname der MySQL-Datenbank
    'user': 'adele',                # Benutzername
    'password': 'Stayless92@',      # Passwort
    'database': 'adcell'            # Datenbankname
}

CHECK_INTERVAL = 10  # Sekunden zwischen den Checks

def create_database_and_table():
    """Erstellt die Datenbank und Tabelle, falls sie nicht existieren."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()

        # Datenbank erstellen
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")

        # Mit der neuen Datenbank verbinden
        connection.database = DB_CONFIG['database']

        # Tabelle erstellen
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS html_tracking (
            id INT AUTO_INCREMENT PRIMARY KEY,
            html_code TEXT NOT NULL,
            status INT DEFAULT NULL
        )
        """)
        print("Database and table ensured.")
        connection.close()

    except Error as e:
        print(f"Error creating database or table: {e}")

async def setup_browser():
    """Richtet den virtuellen Browser ein."""
    browser = await launch(
        headless=True,  # Headless-Modus (kein GUI)
        args=['--no-sandbox', '--disable-setuid-sandbox'],  # Für Hosting-Umgebungen erforderlich
    )
    return browser

async def open_html_in_browser(browser, html_code):
    """Öffnet den HTML-Code in einem virtuellen Browser."""
    page = await browser.newPage()
    try:
        await page.goto(f"data:text/html;charset=utf-8,{html_code}", timeout=10000)
        await asyncio.sleep(2)  # Wartezeit für das Triggern
        print("HTML code triggered successfully.")
    except Exception as e:
        print(f"Error triggering HTML code: {e}")
    finally:
        await page.close()

async def check_and_trigger(browser):
    """Überprüft die Datenbank und triggert neue Einträge."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)

        # Nur neue Einträge mit `status` NULL abrufen
        cursor.execute("SELECT id, html_code FROM html_tracking WHERE status IS NULL")
        rows = cursor.fetchall()

        for row in rows:
            entry_id = row['id']
            html_code = row['html_code']
            print(f"Processing entry ID {entry_id}...")

            await open_html_in_browser(browser, html_code)

            # Status auf 2 setzen, nachdem der Code getriggert wurde
            cursor.execute("UPDATE html_tracking SET status = 2 WHERE id = %s", (entry_id,))
            connection.commit()

        connection.close()

    except Error as e:
        print(f"Database error: {e}")

async def main():
    print("Starting virtual browser tracking tool...")
    create_database_and_table()
    browser = await setup_browser()

    try:
        while True:
            await check_and_trigger(browser)
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("Stopping tracking tool...")
    finally:
        await browser.close()

# Starte das Hauptprogramm
if __name__ == "__main__":
    asyncio.run(main())