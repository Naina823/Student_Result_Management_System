import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
import re

class StudentSystemWithLogin:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Result System - Login")
        self.root.geometry("400x300")
        self.current_user = None
        self.main_window = None
        self.connect_database()
        self.create_login_interface()
    
    def connect_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                port=" give your own port",
                user="root",
                password="your own password",
                database="your own database"
            )
            self.cursor = self.db.cursor()
            self.create_tables()
        except mysql.connector.Error:
            try:
                temp_db = mysql.connector.connect(
                    host="localhost",
                    port="give your own port",
                    user="root",
                    password="your own password"
                )
                temp_cursor = temp_db.cursor()
                temp_cursor.execute("CREATE DATABASE school_db")
                temp_db.commit()
                temp_cursor.close()
                temp_db.close()
                
                self.db = mysql.connector.connect(
                    host="localhost",
                    port="give your own port",
                    user="root",
                    password="your own password",
                    database="your own database"
                )
                self.cursor = self.db.cursor()
                self.create_tables()
            except Exception as e:
                messagebox.showerror("Error", f"Database connection failed: {e}")
                self.root.destroy()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_tables(self):
        # Create users table for login
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create students table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                class VARCHAR(20),
                roll_no VARCHAR(20) UNIQUE
            )
        """)
        
        # Create marks table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                subject VARCHAR(50),
                marks INT,
                skill VARCHAR(50),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        """)
        
        # Insert default admin user if no users exist
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            default_password = self.hash_password("admin123")
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                              ("admin", default_password, "admin"))
            
            # Add a sample teacher user
            teacher_password = self.hash_password("teacher123")
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                              ("teacher", teacher_password, "user"))
        
        self.db.commit()
    
    def create_login_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        title = tk.Label(self.root, text="Student Result Management System",
                     font=("Arial", 16, "bold"), bg="lightblue")
        title.pack(fill=tk.X, pady=10)

        # Login frame
        login_frame = tk.Frame(self.root)
        login_frame.pack(expand=True, pady=20)

        tk.Label(login_frame, text="Login", font=("Arial", 18, "bold")).pack(pady=10)

        # Username
        tk.Label(login_frame, text="Username:", font=("Arial", 12)).pack()
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=25)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(login_frame, text="Password:", font=("Arial", 12)).pack()
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.pack(pady=5)

        # Login button
        tk.Button(login_frame, text="Login", command=self.login,
              font=("Arial", 12, "bold"), bg="green", fg="white", width=15).pack(pady=10)

        # Change password button
        tk.Button(login_frame, text="Change Password", command=self.show_change_password,
              font=("Arial", 10), bg="orange", fg="white", width=15).pack(pady=5)

        # Default credentials info
        info_frame = tk.Frame(self.root)
        info_frame.pack(side=tk.BOTTOM, pady=10)

        tk.Label(info_frame, text="Default Credentials:", font=("Arial", 10, "bold")).pack()
        tk.Label(info_frame, text="Admin: admin / admin123", font=("Arial", 9)).pack()
        tk.Label(info_frame, text="Teacher: teacher / teacher123", font=("Arial", 9)).pack()
 
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())

        print("Login UI fully loaded")
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        try:
            hashed_password = self.hash_password(password)
            query = "SELECT id, username, role FROM users WHERE username = %s AND password = %s"
            self.cursor.execute(query, (username, hashed_password))
            user = self.cursor.fetchone()
            
            if user:
                self.current_user = {
                    'id': user[0],
                    'username': user[1],
                    'role': user[2]
                }
                messagebox.showinfo("Success", f"Welcome, {username}!")
                self.open_main_system()
            else:
                messagebox.showerror("Error", "Invalid username or password!")
                self.password_entry.delete(0, tk.END)
        
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
    
    def show_change_password(self):
        # Create change password window
        change_window = tk.Toplevel(self.root)
        change_window.title("Change Password")
        change_window.geometry("400x300")
        change_window.grab_set()
        
        tk.Label(change_window, text="Change Password", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Username
        tk.Label(change_window, text="Username:", font=("Arial", 12)).pack()
        username_entry = tk.Entry(change_window, font=("Arial", 12), width=25)
        username_entry.pack(pady=5)
        
        # Current password
        tk.Label(change_window, text="Current Password:", font=("Arial", 12)).pack()
        current_password_entry = tk.Entry(change_window, font=("Arial", 12), width=25, show="*")
        current_password_entry.pack(pady=5)
        
        # New password
        tk.Label(change_window, text="New Password:", font=("Arial", 12)).pack()
        new_password_entry = tk.Entry(change_window, font=("Arial", 12), width=25, show="*")
        new_password_entry.pack(pady=5)
        
        # Confirm new password
        tk.Label(change_window, text="Confirm New Password:", font=("Arial", 12)).pack()
        confirm_password_entry = tk.Entry(change_window, font=("Arial", 12), width=25, show="*")
        confirm_password_entry.pack(pady=5)
        
        def change_password():
            username = username_entry.get().strip()
            current_password = current_password_entry.get().strip()
            new_password = new_password_entry.get().strip()
            confirm_password = confirm_password_entry.get().strip()
            
            if not all([username, current_password, new_password, confirm_password]):
                messagebox.showerror("Error", "Please fill all fields!")
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Error", "New passwords do not match!")
                return
            
            if len(new_password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long!")
                return
            
            try:
                # Verify current password
                hashed_current = self.hash_password(current_password)
                self.cursor.execute("SELECT id FROM users WHERE username = %s AND password = %s", 
                                  (username, hashed_current))
                user = self.cursor.fetchone()
                
                if not user:
                    messagebox.showerror("Error", "Invalid username or current password!")
                    return
                
                # Update password
                hashed_new = self.hash_password(new_password)
                self.cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                                  (hashed_new, user[0]))
                self.db.commit()
                
                messagebox.showinfo("Success", "Password changed successfully!")
                change_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {e}")
        
        tk.Button(change_window, text="Change Password", command=change_password,
                 font=("Arial", 12, "bold"), bg="blue", fg="white").pack(pady=20)
        
        tk.Button(change_window, text="Cancel", command=change_window.destroy,
                 font=("Arial", 10), bg="gray", fg="white").pack(pady=5)
    
    def open_main_system(self):
        # Hide login window
        self.root.withdraw()
        
        # Create main system window
        self.main_window = tk.Toplevel()
        self.main_window.title(f"Student Result System - {self.current_user['username']} ({self.current_user['role']})")
        self.main_window.geometry("900x650")
        self.main_window.protocol("WM_DELETE_WINDOW", self.logout)
        
        # Create the main system interface
        self.create_main_interface()
    
    def create_main_interface(self):
        # Title with user info
        title_text = f"Student Result Management System - Welcome, {self.current_user['username']}"
        title = tk.Label(self.main_window, text=title_text,
                        font=("Arial", 16, "bold"), bg="lightblue")
        title.pack(fill=tk.X, pady=5)
        
        # Logout button
        logout_frame = tk.Frame(self.main_window)
        logout_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(logout_frame, text="Logout", command=self.logout,
                 font=("Arial", 10), bg="red", fg="white").pack(side=tk.RIGHT)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_add_student_tab()
        self.create_add_marks_tab()
        self.create_view_results_tab()
        self.create_search_tab()
    
    def logout(self):
        if self.main_window:
            self.main_window.destroy()
        self.current_user = None
        self.root.deiconify()
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
    
    def create_add_student_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Student")
        
        tk.Label(frame, text="Add New Student", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(frame, text="Student Name:", font=("Arial", 12)).pack()
        self.name_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.name_entry.pack(pady=5)
        
        tk.Label(frame, text="Class:", font=("Arial", 12)).pack()
        self.class_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.class_entry.pack(pady=5)
        
        tk.Label(frame, text="Roll Number:", font=("Arial", 12)).pack()
        self.roll_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.roll_entry.pack(pady=5)
        
        tk.Button(frame, text="Add Student", command=self.add_student,
                 font=("Arial", 12, "bold"), bg="green", fg="white").pack(pady=10)
        
        tk.Button(frame, text="Update Selected Student", command=self.update_student,
                 font=("Arial", 10), bg="orange", fg="white").pack(pady=(5, 2))
        
        tk.Button(frame, text="Delete Selected Student", command=self.delete_student,
                 font=("Arial", 10), bg="red", fg="white").pack(pady=(2, 10))
        
        tk.Label(frame, text="All Students:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        self.students_listbox = tk.Listbox(frame, height=10, font=("Arial", 10))
        self.students_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.refresh_students_list()
    
    def add_student(self):
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        roll_no = self.roll_entry.get().strip()
        
        if not name or not class_name or not roll_no:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        try:
            query = "INSERT INTO students (name, class, roll_no) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (name, class_name, roll_no))
            self.db.commit()
            messagebox.showinfo("Success", "Student added successfully!")
            
            self.name_entry.delete(0, tk.END)
            self.class_entry.delete(0, tk.END)
            self.roll_entry.delete(0, tk.END)
            self.refresh_students_list()
            self.load_students_combo()
            self.load_result_combo()

            
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Roll number already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")
    
    def update_student(self):
        selected = self.students_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to update.")
            return
        
        selected_text = self.students_listbox.get(selected[0])
        student_id = int(selected_text.split("ID: ")[1].split(" |")[0])
        
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        roll_no = self.roll_entry.get().strip()
        
        if not name or not class_name or not roll_no:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        try:
            query = "UPDATE students SET name = %s, class = %s, roll_no = %s WHERE id = %s"
            self.cursor.execute(query, (name, class_name, roll_no, student_id))
            self.db.commit()
            messagebox.showinfo("Success", "Student updated successfully!")
            self.refresh_students_list()
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")
    
    def delete_student(self):
        selected = self.students_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this student and all their marks?")
        if not confirm:
            return
        
        selected_text = self.students_listbox.get(selected[0])
        student_id = int(selected_text.split("ID: ")[1].split(" |")[0])
        
        try:
            query = "DELETE FROM students WHERE id = %s"
            self.cursor.execute(query, (student_id,))
            self.db.commit()
            messagebox.showinfo("Success", "Student and their marks deleted!")
            self.refresh_students_list()
            self.load_students_combo()
            self.load_result_combo()

        except Exception as e:
            messagebox.showerror("Error", f"Deletion failed: {e}")
    
    def refresh_students_list(self):
        self.students_listbox.delete(0, tk.END)
        try:
            self.cursor.execute("SELECT id, name, class, roll_no FROM students")
            students = self.cursor.fetchall()
            
            for student in students:
                student_info = f"ID: {student[0]} | {student[1]} | Class: {student[2]} | Roll: {student[3]}"
                self.students_listbox.insert(tk.END, student_info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")
    
    def create_add_marks_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Marks")
        
        tk.Label(frame, text="Add / Update Student Marks", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(frame, text="Select Student:", font=("Arial", 12)).pack()
        self.student_combo = ttk.Combobox(frame, font=("Arial", 12), width=40, state="readonly")
        self.student_combo.pack(pady=5)
        self.load_students_combo()
        
        self.subjects_listbox = tk.Listbox(frame, height=5, font=("Arial", 10))
        self.subjects_listbox.pack(pady=5)
        self.subjects_listbox.bind("<<ListboxSelect>>", self.load_selected_subject_data)
        
        tk.Button(frame, text="Load Subjects", command=self.load_student_subjects).pack(pady=2)
        
        tk.Label(frame, text="Subject:", font=("Arial", 12)).pack()
        self.subject_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.subject_entry.pack(pady=5)
        
        tk.Label(frame, text="Marks (out of 100):", font=("Arial", 12)).pack()
        self.marks_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.marks_entry.pack(pady=5)
        
        tk.Label(frame, text="Skill (e.g., Python, Java):", font=("Arial", 12)).pack()
        self.skill_entry = tk.Entry(frame, font=("Arial", 12), width=30)
        self.skill_entry.pack(pady=5)
        
        tk.Button(frame, text="Add Marks", command=self.add_marks,
                 font=("Arial", 12, "bold"), bg="blue", fg="white").pack(pady=5)
        
        tk.Button(frame, text="Update Selected Marks", command=self.update_marks,
                 font=("Arial", 10), bg="orange", fg="white").pack(pady=2)
        
        tk.Button(frame, text="Delete Selected Marks", command=self.delete_marks,
                 font=("Arial", 10), bg="red", fg="white").pack(pady=2)
    
    def load_students_combo(self):
        try:
            self.cursor.execute("SELECT id, name, roll_no FROM students")
            students = self.cursor.fetchall()
            student_list = [f"{s[1]} (Roll: {s[2]}) - ID: {s[0]}" for s in students]
            self.student_combo['values'] = student_list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")
    
    def load_student_subjects(self):
        self.subjects_listbox.delete(0, tk.END)
        if not self.student_combo.get():
            return
        
        try:
            student_id = int(self.student_combo.get().split("ID: ")[1])
            self.cursor.execute("SELECT subject FROM marks WHERE student_id = %s", (student_id,))
            subjects = self.cursor.fetchall()
            for subject in subjects:
                self.subjects_listbox.insert(tk.END, subject[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subjects: {e}")
    
    def load_selected_subject_data(self, event):
        try:
            subject_name = self.subjects_listbox.get(self.subjects_listbox.curselection())
            student_id = int(self.student_combo.get().split("ID: ")[1])
            
            self.cursor.execute("SELECT subject, marks, skill FROM marks WHERE student_id = %s AND subject = %s",
                               (student_id, subject_name))
            data = self.cursor.fetchone()
            
            if data:
                self.subject_entry.delete(0, tk.END)
                self.marks_entry.delete(0, tk.END)
                self.skill_entry.delete(0, tk.END)
                
                self.subject_entry.insert(0, data[0])
                self.marks_entry.insert(0, data[1])
                self.skill_entry.insert(0, data[2])
        except:
            pass
    
    def add_marks(self):
        if not self.student_combo.get():
            messagebox.showerror("Error", "Please select a student!")
            return
        
        subject = self.subject_entry.get().strip()
        marks_text = self.marks_entry.get().strip()
        skill = self.skill_entry.get().strip()
        
        if not subject or not marks_text or not skill:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        try:
            marks = int(marks_text)
            if marks < 0 or marks > 100:
                messagebox.showerror("Error", "Marks must be between 0 and 100!")
                return
            
            selected_text = self.student_combo.get()
            student_id = int(selected_text.split("ID: ")[1])
            
            query = "INSERT INTO marks (student_id, subject, marks, skill) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (student_id, subject, marks, skill))
            self.db.commit()
            messagebox.showinfo("Success", f"Marks added for {subject}!")
            
            self.subject_entry.delete(0, tk.END)
            self.marks_entry.delete(0, tk.END)
            self.skill_entry.delete(0, tk.END)
            self.load_student_subjects()
            
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Duplicate entry!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add marks: {e}")
    
    def update_marks(self):
        try:
            student_id = int(self.student_combo.get().split("ID: ")[1])
            selected_subject = self.subjects_listbox.get(self.subjects_listbox.curselection())
            
            new_subject = self.subject_entry.get().strip()
            new_marks = int(self.marks_entry.get().strip())
            new_skill = self.skill_entry.get().strip()
            
            if not new_subject or not new_skill:
                messagebox.showerror("Error", "All fields required!")
                return
            
            query = "UPDATE marks SET subject=%s, marks=%s, skill=%s WHERE student_id=%s AND subject=%s"
            self.cursor.execute(query, (new_subject, new_marks, new_skill, student_id, selected_subject))
            self.db.commit()
            messagebox.showinfo("Success", "Marks updated!")
            self.load_student_subjects()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}")
    
    def delete_marks(self):
        try:
            subject = self.subjects_listbox.get(self.subjects_listbox.curselection())
            student_id = int(self.student_combo.get().split("ID: ")[1])
            
            self.cursor.execute("DELETE FROM marks WHERE student_id = %s AND subject = %s", 
                               (student_id, subject))
            self.db.commit()
            messagebox.showinfo("Deleted", "Marks deleted.")
            self.load_student_subjects()
            
            self.subject_entry.delete(0, tk.END)
            self.marks_entry.delete(0, tk.END)
            self.skill_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")
    
    def create_view_results_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="View Results")
        
        tk.Label(frame, text="View Student Results", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(frame, text="Select Student:", font=("Arial", 12)).pack()
        self.result_combo = ttk.Combobox(frame, font=("Arial", 12), width=40, state="readonly")
        self.result_combo.pack(pady=5)
        self.load_result_combo()
        
        tk.Button(frame, text="View Result", command=self.view_result,
                 font=("Arial", 12, "bold"), bg="orange", fg="white").pack(pady=10)
        
        self.result_text = tk.Text(frame, height=20, width=75, font=("Arial", 11))
        self.result_text.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    
    def load_result_combo(self):
        try:
            self.cursor.execute("SELECT id, name, roll_no FROM students")
            students = self.cursor.fetchall()
            student_list = [f"{s[1]} (Roll: {s[2]}) - ID: {s[0]}" for s in students]
            self.result_combo.set('')
            self.result_combo['values'] = student_list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students: {e}")
    
    def view_result(self):
        if not self.result_combo.get():
            messagebox.showerror("Error", "Please select a student!")
            return
        
        try:
            student_id = int(self.result_combo.get().split("ID: ")[1])
            
            self.cursor.execute("SELECT name, class, roll_no FROM students WHERE id = %s", (student_id,))
            student = self.cursor.fetchone()
            
            self.cursor.execute("SELECT subject, marks, skill FROM marks WHERE student_id = %s", (student_id,))
            marks = self.cursor.fetchall()
            
            self.result_text.delete(1.0, tk.END)
            
            if not marks:
                self.result_text.insert(tk.END, "No marks found for this student!")
                return
            
            result_text = f"STUDENT RESULT CARD\n{'='*50}\n\n"
            result_text += f"Name: {student[0]}\nClass: {student[1]}\nRoll No: {student[2]}\n\n"
            result_text += f"MARKS & SKILLS:\n{'-'*40}\n"
            
            total_marks = 0
            total_subjects = len(marks)
            
            for subject, mark, skill in marks:
                result_text += f"{subject}: {mark}/100 | Skill: {skill}\n"
                total_marks += mark
            
            percentage = (total_marks / (total_subjects * 100)) * 100
            
            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            elif percentage >= 50:
                grade = "D"
            else:
                grade = "F"
            
            if percentage >= 75:
                strength = "Strong in academics"
            elif percentage >= 50:
                strength = "Average in academics"
            else:
                strength = "Needs improvement"
            
            result_text += f"\n{'-'*40}\n"
            result_text += f"Total Marks: {total_marks}/{total_subjects * 100}\n"
            result_text += f"Percentage: {percentage:.2f}%\n"
            result_text += f"Grade: {grade}\n"
            result_text += f"Academic Performance: {strength}\n"
            
            self.result_text.insert(tk.END, result_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch results: {e}")

    def create_search_tab(self):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text="Smart Search")

        tk.Label(frame, text="Enter your query (e.g., 'marks above 80', 'skill Python')", 
                 font=("Arial", 14, "bold")).pack(pady=10)

        self.search_entry = tk.Entry(frame, font=("Arial", 12), width=50)
        self.search_entry.pack(pady=5)

        tk.Button(
            frame, text="Search", command=self.smart_search,
            font=("Arial", 12, "bold"), bg="blue", fg="white"
        ).pack(pady=5)

        self.search_listbox = tk.Listbox(frame, font=("Arial", 11), width=85, height=15)
        self.search_listbox.pack(pady=10)

    def smart_search(self):
        query = self.search_entry.get().strip().lower()
        self.search_listbox.delete(0, tk.END)

        if not query:
            messagebox.showerror("Error", "Please enter a query.")
            return

        try:
            # Debug: print the query
            print("Query received:", query)

            results = []
            if "marks above" in query:
                value = int(query.split("marks above")[1].strip())
                sql = """
                    SELECT s.id, s.name, s.class, s.roll_no, m.subject, m.marks, m.skill
                    FROM students s
                    JOIN marks m ON s.id = m.student_id
                    WHERE m.marks >= %s
                """
                self.cursor.execute(sql, (value,))
                results = self.cursor.fetchall()

            elif "marks below" in query:
                value = int(query.split("marks below")[1].strip())
                sql = """
                    SELECT s.id, s.name, s.class, s.roll_no, m.subject, m.marks, m.skill
                    FROM students s
                    JOIN marks m ON s.id = m.student_id
                    WHERE m.marks <= %s
                """
                self.cursor.execute(sql, (value,))
                results = self.cursor.fetchall()

            elif "skill" in query:
                skill = query.split("skill")[-1].strip()
                sql = """
                    SELECT s.id, s.name, s.class, s.roll_no, m.subject, m.marks, m.skill
                    FROM students s
                    JOIN marks m ON s.id = m.student_id
                    WHERE m.skill LIKE %s
                """
                self.cursor.execute(sql, (f"%{skill}%",))
                results = self.cursor.fetchall()

            elif "subject" in query:
                subject = query.split("subject")[-1].strip()
                sql = """
                    SELECT s.id, s.name, s.class, s.roll_no, m.subject, m.marks, m.skill
                    FROM students s
                    JOIN marks m ON s.id = m.student_id
                    WHERE m.subject LIKE %s
                """
                self.cursor.execute(sql, (f"%{subject}%",))
                results = self.cursor.fetchall()

            else:
                self.cursor.execute("""
                    SELECT id, name, class, roll_no 
                    FROM students 
                    WHERE name LIKE %s OR class LIKE %s OR roll_no LIKE %s
                """, (f"%{query}%", f"%{query}%", f"%{query}%"))
                students = self.cursor.fetchall()

                if not students:
                    self.search_listbox.insert(tk.END, "No matching records found.")
                else:
                    for student in students:
                        info = f"ID: {student[0]} | Name: {student[1]} | Class: {student[2]} | Roll: {student[3]}"
                        self.search_listbox.insert(tk.END, info)
                return  # fallback done

            # Show marks-related results
            if not results:
                self.search_listbox.insert(tk.END, "No matching records found.")
            else:
                for row in results:
                    info = f"ID: {row[0]} | Name: {row[1]} | Class: {row[2]} | Roll: {row[3]} | Subject: {row[4]} | Marks: {row[5]} | Skill: {row[6]}"
                    self.search_listbox.insert(tk.END, info)

        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")
            print("Search error:", e)

if __name__ == "__main__":
    app = StudentSystemWithLogin()
    app.root.mainloop()

