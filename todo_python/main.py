

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import json


class Task:
    """Represents a single task item"""
    def __init__(self, name, priority="Low", due_date="", category="Personal", status="Pending"):
        self.name = name
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.status = status

    def to_dict(self):
        """Convert task to dictionary for JSON storage"""
        return {
            "name": self.name,
            "priority": self.priority,
            "due_date": self.due_date,
            "category": self.category,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        """Create Task from dictionary"""
        return Task(
            name=data["name"],
            priority=data["priority"],
            due_date=data["due_date"],
            category=data["category"],
            status=data["status"]
        )

    def __str__(self):
        return f"{self.name} | {self.priority} | {self.due_date} | {self.category} | {self.status}"


class TaskStorage:
    """Handles saving and loading tasks from file"""

    def __init__(self, username):
        self.username = username
        self.filename = f"{username}_tasks.json"

    def save_tasks(self, tasks):
        """Save tasks to JSON file"""
        data = [task.to_dict() for task in tasks]
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_tasks(self):
        """Load tasks from JSON file"""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []


class LoginWindow:
    """Login window for user authentication"""

    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("To-Do List - Login")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        # Center the window
        self.center_window()

        self.create_widgets()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 400
        height = 250
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Create login form widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="To-Do List Login",
                                font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=(0, 30))

        # Username frame
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=10)

        ttk.Label(username_frame, text="Username:", font=('Helvetica', 11)).pack(anchor=tk.W)
        self.username_entry = ttk.Entry(username_frame, font=('Helvetica', 11), width=30)
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        self.username_entry.bind('<Return>', lambda e: self.login())

        # Login button
        login_btn = ttk.Button(main_frame, text="Login", command=self.login)
        login_btn.pack(pady=30)

        # Focus on username entry
        self.username_entry.focus()

    def login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()

        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return

        if not username.isalnum():
            messagebox.showerror("Error", "Username must contain only letters and numbers")
            return

        # Clear login window and proceed
        for widget in self.root.winfo_children():
            widget.destroy()

        self.on_login_success(username)


class ToDoApp:
    """Main To-Do List Application"""

    CATEGORIES = ["Work", "Personal", "Study", "Shopping", "Health", "Other"]
    PRIORITIES = ["High", "Low"]

    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.storage = TaskStorage(username)
        self.tasks = self.storage.load_tasks()
        self.selected_index = None

        self.root.title(f"To-Do List - {username}")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        self.create_widgets()
        self.refresh_task_list()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Configure style
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'))

        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text=f"Welcome, {self.username}!",
                  style='Title.TLabel').pack(side=tk.LEFT)

        ttk.Button(header_frame, text="Logout",
                   command=self.logout).pack(side=tk.RIGHT)

        # Content frame (left: form, right: task list)
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Task input form
        left_panel = ttk.LabelFrame(content_frame, text="Task Details", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Task Name
        ttk.Label(left_panel, text="Task Name:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.task_name_entry = ttk.Entry(left_panel, width=30, font=('Helvetica', 10))
        self.task_name_entry.grid(row=1, column=0, pady=(0, 15), sticky=tk.EW)

        # Priority
        ttk.Label(left_panel, text="Priority:", style='Header.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.priority_var = tk.StringVar(value="Low")
        self.priority_combo = ttk.Combobox(left_panel, textvariable=self.priority_var,
                                           values=self.PRIORITIES, state="readonly", width=28)
        self.priority_combo.grid(row=3, column=0, pady=(0, 15), sticky=tk.EW)

        # Due Date
        ttk.Label(left_panel, text="Due Date (YYYY-MM-DD):", style='Header.TLabel').grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.due_date_entry = ttk.Entry(left_panel, width=30, font=('Helvetica', 10))
        self.due_date_entry.grid(row=5, column=0, pady=(0, 15), sticky=tk.EW)

        # Category
        ttk.Label(left_panel, text="Category:", style='Header.TLabel').grid(
            row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.category_var = tk.StringVar(value="Personal")
        self.category_combo = ttk.Combobox(left_panel, textvariable=self.category_var,
                                           values=self.CATEGORIES, state="readonly", width=28)
        self.category_combo.grid(row=7, column=0, pady=(0, 20), sticky=tk.EW)

        # Buttons frame
        buttons_frame = ttk.Frame(left_panel)
        buttons_frame.grid(row=8, column=0, pady=(0, 10))

        ttk.Button(buttons_frame, text="Add Task",
                   command=self.add_task, width=12).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(buttons_frame, text="Update Task",
                   command=self.update_task, width=12).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(buttons_frame, text="Delete Task",
                   command=self.delete_task, width=12).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(buttons_frame, text="Mark Complete",
                   command=self.mark_completed, width=12).grid(row=1, column=1, padx=2, pady=2)

        # Clear button
        ttk.Button(left_panel, text="Clear Form",
                   command=self.clear_form).grid(row=9, column=0, pady=(10, 0))

        # Right panel - Task list
        right_panel = ttk.LabelFrame(content_frame, text="Tasks", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Treeview for tasks
        columns = ("Name", "Priority", "Due Date", "Category", "Status")
        self.task_tree = ttk.Treeview(right_panel, columns=columns, show="headings",
                                       selectmode="browse")

        # Configure columns
        self.task_tree.heading("Name", text="Task Name")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Due Date", text="Due Date")
        self.task_tree.heading("Category", text="Category")
        self.task_tree.heading("Status", text="Status")

        self.task_tree.column("Name", width=200, minwidth=150)
        self.task_tree.column("Priority", width=80, minwidth=60)
        self.task_tree.column("Due Date", width=100, minwidth=80)
        self.task_tree.column("Category", width=100, minwidth=80)
        self.task_tree.column("Status", width=100, minwidth=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL,
                                  command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)

        # Configure tag colors for status
        self.task_tree.tag_configure('completed', foreground='green')
        self.task_tree.tag_configure('pending_high', foreground='red')
        self.task_tree.tag_configure('pending_low', foreground='black')

        # Status bar
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT)

        self.task_count_label = ttk.Label(status_frame, text="")
        self.task_count_label.pack(side=tk.RIGHT)

    def refresh_task_list(self):
        """Refresh the task list display"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # Add tasks to treeview
        for i, task in enumerate(self.tasks):
            # Determine tag based on status and priority
            if task.status == "Completed":
                tag = 'completed'
            elif task.priority == "High":
                tag = 'pending_high'
            else:
                tag = 'pending_low'

            self.task_tree.insert("", tk.END, iid=i, values=(
                task.name, task.priority, task.due_date, task.category, task.status
            ), tags=(tag,))

        # Update task count
        pending = sum(1 for t in self.tasks if t.status == "Pending")
        completed = sum(1 for t in self.tasks if t.status == "Completed")
        self.task_count_label.config(
            text=f"Total: {len(self.tasks)} | Pending: {pending} | Completed: {completed}"
        )

    def on_task_select(self, event):
        """Handle task selection in treeview"""
        selection = self.task_tree.selection()
        if selection:
            self.selected_index = int(selection[0])
            task = self.tasks[self.selected_index]

            # Populate form with selected task data
            self.task_name_entry.delete(0, tk.END)
            self.task_name_entry.insert(0, task.name)
            self.priority_var.set(task.priority)
            self.due_date_entry.delete(0, tk.END)
            self.due_date_entry.insert(0, task.due_date)
            self.category_var.set(task.category)

            self.status_label.config(text=f"Selected: {task.name}")

    def validate_date(self, date_str):
        """Validate date format (YYYY-MM-DD)"""
        if not date_str:
            return True  # Empty date is allowed
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def get_form_data(self):
        """Get data from form fields"""
        name = self.task_name_entry.get().strip()
        priority = self.priority_var.get()
        due_date = self.due_date_entry.get().strip()
        category = self.category_var.get()

        return name, priority, due_date, category

    def add_task(self):
        """Add a new task"""
        name, priority, due_date, category = self.get_form_data()

        # Validation
        if not name:
            messagebox.showerror("Error", "Task name is required")
            return

        if not self.validate_date(due_date):
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        # Create and add task
        task = Task(name, priority, due_date, category, "Pending")
        self.tasks.append(task)

        # Save and refresh
        self.storage.save_tasks(self.tasks)
        self.refresh_task_list()
        self.clear_form()

        self.status_label.config(text=f"Task '{name}' added successfully")
        messagebox.showinfo("Success", "Task added successfully!")

    def update_task(self):
        """Update the selected task"""
        if self.selected_index is None:
            messagebox.showerror("Error", "Please select a task to update")
            return

        name, priority, due_date, category = self.get_form_data()

        # Validation
        if not name:
            messagebox.showerror("Error", "Task name is required")
            return

        if not self.validate_date(due_date):
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        # Update task
        task = self.tasks[self.selected_index]
        task.name = name
        task.priority = priority
        task.due_date = due_date
        task.category = category

        # Save and refresh
        self.storage.save_tasks(self.tasks)
        self.refresh_task_list()

        self.status_label.config(text=f"Task '{name}' updated successfully")
        messagebox.showinfo("Success", "Task updated successfully!")

    def delete_task(self):
        """Delete the selected task"""
        if self.selected_index is None:
            messagebox.showerror("Error", "Please select a task to delete")
            return

        task = self.tasks[self.selected_index]

        # Confirm deletion
        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to delete '{task.name}'?"):
            del self.tasks[self.selected_index]

            # Save and refresh
            self.storage.save_tasks(self.tasks)
            self.refresh_task_list()
            self.clear_form()

            self.status_label.config(text=f"Task deleted successfully")
            self.selected_index = None

    def mark_completed(self):
        """Mark the selected task as completed"""
        if self.selected_index is None:
            messagebox.showerror("Error", "Please select a task to mark as completed")
            return

        task = self.tasks[self.selected_index]

        if task.status == "Completed":
            messagebox.showinfo("Info", "This task is already completed")
            return

        task.status = "Completed"

        # Save and refresh
        self.storage.save_tasks(self.tasks)
        self.refresh_task_list()

        self.status_label.config(text=f"Task '{task.name}' marked as completed")
        messagebox.showinfo("Success", "Task marked as completed!")

    def clear_form(self):
        """Clear all form fields"""
        self.task_name_entry.delete(0, tk.END)
        self.priority_var.set("Low")
        self.due_date_entry.delete(0, tk.END)
        self.category_var.set("Personal")
        self.selected_index = None

        # Clear selection in treeview
        for item in self.task_tree.selection():
            self.task_tree.selection_remove(item)

        self.status_label.config(text="Form cleared")

    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Clear current window
            for widget in self.root.winfo_children():
                widget.destroy()

            # Show login window
            LoginWindow(self.root, self.on_login)

    def on_login(self, username):
        """Callback when user logs in again"""
        self.__init__(self.root, username)


def main():
    """Main entry point"""
    root = tk.Tk()

    def on_login_success(username):
        ToDoApp(root, username)

    LoginWindow(root, on_login_success)

    root.mainloop()


if __name__ == "__main__":
    main()
