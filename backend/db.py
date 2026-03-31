import mysql.connector
from datetime import datetime

class DatabaseService:
    @staticmethod
    def create_connection():
        """Create and return a new DB connection"""
        return mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="Ujjwalsql@2500",
            database="Test1"
        )

    @staticmethod
    def init_tables():
        conn = DatabaseService.create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS take2 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                names VARCHAR(100),
                roll_no VARCHAR(20) UNIQUE,
                course VARCHAR(50),
                image LONGBLOB
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                roll_no VARCHAR(20),
                date_time DATETIME,
                FOREIGN KEY (roll_no) REFERENCES take2(roll_no) ON DELETE CASCADE
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all_students():
        """Return all student records with images (used for training)."""
        conn = DatabaseService.create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT roll_no, names, image, course FROM take2")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def register_student(name, roll, course, image_bytes=None):
        """Register a new student (with optional image)."""
        conn = DatabaseService.create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO take2 (names, roll_no, course, image) VALUES (%s, %s, %s, %s)",
                (name, roll, course, image_bytes)
            )
            conn.commit()
            return {"success": True, "message": "Student registered successfully"}
        except mysql.connector.IntegrityError:
            return {"success": False, "message": "Roll number already exists"}
        except Exception as e:
            print(f"register_student error: {e}")
            return {"success": False, "message": str(e)}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_student_by_roll(roll):
        conn = DatabaseService.create_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("SELECT * FROM take2 WHERE roll_no=%s", (roll,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_student_name_by_roll(roll):
        conn = DatabaseService.create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT names FROM take2 WHERE roll_no=%s", (roll,))
            result = cursor.fetchone()
            return result[0] if result else "Unknown"
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def check_attendance_today(roll):
        conn = DatabaseService.create_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            now = datetime.now()
            cursor.execute(
                "SELECT * FROM attendance WHERE roll_no=%s AND DATE(date_time)=DATE(%s)",
                (roll, now)
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def mark_attendance(roll):
        conn = DatabaseService.create_connection()
        cursor = conn.cursor()
        try:
            now = datetime.now()
            cursor.execute(
                "INSERT INTO attendance (roll_no, date_time) VALUES (%s, %s)",
                (roll, now)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"mark_attendance error: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_attendance_records(roll):
        conn = DatabaseService.create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT date_time FROM attendance WHERE roll_no=%s ORDER BY date_time DESC",
                (roll,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def get_todays_attendance_records():
        """Fetch all attendance records for today along with student names."""
        conn = DatabaseService.create_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT t.names, t.roll_no, a.date_time
                FROM attendance a
                JOIN take2 t ON a.roll_no = t.roll_no
                WHERE DATE(a.date_time) = CURDATE()
                ORDER BY a.date_time DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"get_todays_attendance_records error: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def clear_tables():
        """Delete all student and attendance data."""
        try:
            conn = DatabaseService.create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance")
            cursor.execute("DELETE FROM take2")
            conn.commit()
            cursor.close()
            conn.close()
            print("All tables cleared.")
        except Exception as e:
            print(f"clear_tables error: {e}")