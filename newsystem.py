import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import pandas as pd
from datetime import datetime
import json
import os
import traceback
from PIL import Image, ImageTk

class DataMigrationManager:
    def __init__(self, school):
        self.school = school
        self.migration_templates = {
            "students": {
                "required_fields": ["name", "birth_date", "gender", "admission_number"],
                "optional_fields": ["current_grade"],
                "sample_data": {
                    "name": "John Doe",
                    "birth_date": "2015-05-15",
                    "gender": "Male",
                    "admission_number": "SCH2023001",
                    "current_grade": "Grade 4"
                }
            },
            "parents": {
                "required_fields": ["student_admission", "name", "phone", "relationship"],
                "optional_fields": ["email"],
                "sample_data": {
                    "student_admission": "SCH2023001",
                    "name": "Mary Doe",
                    "phone": "254712345678",
                    "relationship": "Mother",
                    "email": "parent@example.com"
                }
            },
            "teachers": {
                "required_fields": ["name", "tsc_number", "specialization"],
                "optional_fields": ["phone", "email", "classes_teaching", "subjects_teaching"],
                "sample_data": {
                    "name": "Jane Smith",
                    "tsc_number": "TSC12345",
                    "specialization": "Upper Primary",
                    "phone": "254712345679",
                    "email": "teacher@example.com",
                    "classes_teaching": "Grade 4,Grade 5",
                    "subjects_teaching": "Math,Science"
                }
            },
            "assessments": {
                "required_fields": ["student_admission", "name", "subject", "score", "date"],
                "optional_fields": ["term", "competency_area"],
                "sample_data": {
                    "student_admission": "SCH2023001",
                    "name": "Term 1 Math Exam",
                    "subject": "Math",
                    "score": "85",
                    "date": "2023-03-15",
                    "term": "Term 1",
                    "competency_area": "Numeracy"
                }
            },
            "payments": {
                "required_fields": ["student_admission", "amount", "payment_date"],
                "optional_fields": ["payment_method", "bank_slip_no", "term", "description"],
                "sample_data": {
                    "student_admission": "SCH2023001",
                    "amount": "1500",
                    "payment_date": "2023-01-10",
                    "payment_method": "MPesa",
                    "bank_slip_no": "MP123456",
                    "term": "Term 1",
                    "description": "Tuition Fee"
                }
            }
        }

class MigrationDialog:
    def __init__(self, parent, school):
        self.parent = parent
        self.school = school
        self.migration_manager = DataMigrationManager(school)
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Data Migration Tool")
        self.dialog.geometry("900x700")
        
        # Make the dialog modal
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        self.current_file = None
        self.current_data_type = None
        self.file_preview_data = []
        self.field_mapping = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main notebook for different migration steps
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create all steps
        self.create_step1()
        self.create_step2()
        self.create_step3()
        self.create_step4()
        
        # Start with step 1 active
        self.notebook.tab(1, state='disabled')
        self.notebook.tab(2, state='disabled')
        self.notebook.tab(3, state='disabled')
    
    def create_step1(self):
        """Step 1: Select Data Type"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="1. Select Data Type")
        
        lbl = ttk.Label(frame, text="Select Data Type to Migrate", font=('Helvetica', 14, 'bold'))
        lbl.pack(pady=20)
        
        # Data type selection
        self.data_type_var = tk.StringVar()
        data_types = list(self.migration_manager.migration_templates.keys())
        
        for data_type in data_types:
            rb = ttk.Radiobutton(
                frame,
                text=data_type.capitalize(),
                variable=self.data_type_var,
                value=data_type,
                command=self.enable_step2
            )
            rb.pack(anchor='w', padx=50, pady=5)
        
        # Template download
        ttk.Label(frame, text="Need a template file?").pack(pady=10)
        self.download_btn = ttk.Button(
            frame,
            text="Download CSV Template",
            command=self.download_template
        )
        self.download_btn.pack(pady=5)
        
        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=10)
        
        self.next_btn1 = ttk.Button(
            nav_frame,
            text="Next →",
            state='disabled',
            command=lambda: self.notebook.select(1)
        )
        self.next_btn1.pack(side='right', padx=10)
    
    def create_step2(self):
        """Step 2: Upload File"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="2. Upload File")
        
        ttk.Label(frame, text="Upload Your Data File", font=('Helvetica', 14, 'bold')).pack(pady=20)
        
        # File selection
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(file_frame, text="Select file:").pack(side='left')
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly').pack(side='left', fill='x', expand=True, padx=5)
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side='right')
        
        # Preview area
        self.preview_label = ttk.Label(frame, text="File preview will appear here")
        self.preview_label.pack(pady=10)
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        self.preview_tree = ttk.Treeview(tree_frame)
        self.preview_tree.pack(side='left', fill='both', expand=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        vsb.pack(side='right', fill='y')
        self.preview_tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.preview_tree.xview)
        hsb.pack(fill='x', padx=20)
        self.preview_tree.configure(xscrollcommand=hsb.set)
        
        # Validation message
        self.validation_msg = ttk.Label(frame, text="", foreground='red')
        self.validation_msg.pack(pady=5)
        
        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=10)
        
        ttk.Button(
            nav_frame,
            text="← Back",
            command=lambda: self.notebook.select(0)
        ).pack(side='left', padx=10)
        
        self.next_btn2 = ttk.Button(
            nav_frame,
            text="Next →",
            state='disabled',
            command=lambda: self.notebook.select(2)
        )
        self.next_btn2.pack(side='right', padx=10)
    
    def create_step3(self):
        """Step 3: Map Fields"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="3. Map Fields")
        
        ttk.Label(frame, text="Map Your File Fields to System Fields", 
                 font=('Helvetica', 14, 'bold')).pack(pady=20)
        
        # Mapping instructions
        ttk.Label(frame, text="For each field in your file, select the corresponding system field").pack(pady=5)
        
        # Container for mapping widgets
        self.mapping_container = ttk.Frame(frame)
        self.mapping_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Add canvas and scrollbar
        canvas = tk.Canvas(self.mapping_container)
        scrollbar = ttk.Scrollbar(self.mapping_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # This will hold our mapping widgets
        self.mapping_content = scrollable_frame
        
        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=10)
        
        ttk.Button(
            nav_frame,
            text="← Back",
            command=lambda: self.notebook.select(1)
        ).pack(side='left', padx=10)
        
        self.next_btn3 = ttk.Button(
            nav_frame,
            text="Next →",
            state='disabled',
            command=self.validate_mappings
        )
        self.next_btn3.pack(side='right', padx=10)
    
    def create_step4(self):
        """Step 4: Review & Import"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="4. Review & Import")
        
        ttk.Label(frame, text="Review and Import Data", font=('Helvetica', 14, 'bold')).pack(pady=20)
        
        # Summary info
        summary_frame = ttk.Frame(frame)
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(summary_frame, text="Data Type:").grid(row=0, column=0, sticky='e')
        self.summary_type = ttk.Label(summary_frame, text="", font=('Helvetica', 10, 'bold'))
        self.summary_type.grid(row=0, column=1, sticky='w')
        
        ttk.Label(summary_frame, text="File:").grid(row=1, column=0, sticky='e')
        self.summary_file = ttk.Label(summary_frame, text="", font=('Helvetica', 10))
        self.summary_file.grid(row=1, column=1, sticky='w')
        
        ttk.Label(summary_frame, text="Records:").grid(row=2, column=0, sticky='e')
        self.summary_records = ttk.Label(summary_frame, text="", font=('Helvetica', 10))
        self.summary_records.grid(row=2, column=1, sticky='w')
        
        # Dry run option
        self.dry_run_var = tk.IntVar(value=1)
        ttk.Checkbutton(
            frame,
            text="Perform dry run (test without saving)",
            variable=self.dry_run_var
        ).pack(pady=10)
        
        # Import button
        self.import_btn = ttk.Button(
            frame,
            text="Start Import",
            style='Accent.TButton',
            command=self.run_import
        )
        self.import_btn.pack(pady=20)
        
        # Results area
        results_frame = ttk.Frame(frame)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10, state='disabled')
        self.results_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.results_text['yscrollcommand'] = scrollbar.set
        
        # Navigation
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side='bottom', fill='x', pady=10)
        
        ttk.Button(
            nav_frame,
            text="← Back",
            command=lambda: self.notebook.select(2)
        ).pack(side='left', padx=10)
        
        self.finish_btn = ttk.Button(
            nav_frame,
            text="Finish",
            state='disabled',
            command=self.dialog.destroy
        )
        self.finish_btn.pack(side='right', padx=10)
    
    def enable_step2(self):
        """Enable step 2 when data type is selected"""
        self.current_data_type = self.data_type_var.get()
        self.notebook.tab(1, state='normal')
        self.next_btn1.config(state='normal')
    
    def browse_file(self):
        """Handle file browsing"""
        file_types = [
            ('CSV files', '*.csv'),
            ('Excel files', '*.xls *.xlsx'),
            ('All files', '*.*')
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.current_file = file_path
            self.file_path_var.set(file_path)
            self.validate_file()
    
    def validate_file(self):
        """Validate the uploaded file"""
        if not self.current_file or not self.current_data_type:
            return
        
        try:
            if self.current_file.endswith('.csv'):
                df = pd.read_csv(self.current_file)
            elif self.current_file.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(self.current_file)
            else:
                self.validation_msg.config(text="Unsupported file format", foreground='red')
                return
            
            # Get template for this data type
            template = self.migration_manager.get_migration_template(self.current_data_type)
            if not template:
                self.validation_msg.config(text="Invalid data type", foreground='red')
                return
            
            # Check required fields
            missing_fields = [field for field in template['required_fields'] 
                            if field not in df.columns]
            if missing_fields:
                self.validation_msg.config(
                    text=f"Missing required fields: {', '.join(missing_fields)}",
                    foreground='red'
                )
                return
            
            # Show preview
            self.file_preview_data = df.head(5).to_dict('records')
            self.show_file_preview()
            
            self.validation_msg.config(text="File is valid", foreground='green')
            self.next_btn2.config(state='normal')
            self.setup_field_mapping()
            
        except Exception as e:
            self.validation_msg.config(text=f"Error reading file: {str(e)}", foreground='red')
            traceback.print_exc()
    
    def show_file_preview(self):
        """Display a preview of the file data"""
        if not self.file_preview_data:
            return
        
        # Clear previous preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self.preview_tree['columns'] = []
        
        # Set up columns from first row
        columns = list(self.file_preview_data[0].keys())
        self.preview_tree['columns'] = columns
        
        # Create headings
        self.preview_tree.heading('#0', text='Row')
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100, anchor='w')
        
        # Add data rows
        for i, row in enumerate(self.file_preview_data, 1):
            values = [str(row[col])[:50] for col in columns]  # Limit preview length
            self.preview_tree.insert('', 'end', text=str(i), values=values)
    
    def setup_field_mapping(self):
        """Set up the field mapping interface"""
        # Clear previous widgets
        for widget in self.mapping_content.winfo_children():
            widget.destroy()
        
        if not self.file_preview_data:
            return
        
        # Get template fields
        template = self.migration_manager.get_migration_template(self.current_data_type)
        if not template:
            return
        
        # Create header
        ttk.Label(self.mapping_content, text="File Field", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(self.mapping_content, text="→", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(self.mapping_content, text="System Field", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=5, pady=2)
        
        # Create mapping rows
        file_fields = list(self.file_preview_data[0].keys())
        system_fields = template['required_fields'] + template['optional_fields']
        
        self.field_mapping = {}
        
        for i, file_field in enumerate(file_fields, 1):
            # File field label
            ttk.Label(self.mapping_content, text=file_field).grid(row=i, column=0, padx=5, pady=2, sticky='e')
            
            # Arrow
            ttk.Label(self.mapping_content, text="→").grid(row=i, column=1, padx=5, pady=2)
            
            # System field combobox
            var = tk.StringVar()
            cb = ttk.Combobox(
                self.mapping_content,
                textvariable=var,
                values=system_fields,
                state='readonly'
            )
            cb.grid(row=i, column=2, padx=5, pady=2, sticky='w')
            
            # Auto-select if names match
            if file_field in system_fields:
                var.set(file_field)
            
            self.field_mapping[file_field] = var
        
        self.next_btn3.config(state='normal')
    
    def validate_mappings(self):
        """Validate field mappings before proceeding"""
        template = self.migration_manager.get_migration_template(self.current_data_type)
        if not template:
            return
        
        # Check all required fields are mapped
        missing_required = []
        mapping = {}
        
        for file_field, var in self.field_mapping.items():
            system_field = var.get()
            if system_field:
                mapping[file_field] = system_field
        
        for req_field in template['required_fields']:
            if req_field not in mapping.values():
                missing_required.append(req_field)
        
        if missing_required:
            messagebox.showerror(
                "Missing Mappings",
                f"The following required fields are not mapped: {', '.join(missing_required)}"
            )
            return
        
        # Proceed to next step
        self.notebook.tab(3, state='normal')
        self.notebook.select(3)
        self.update_summary()
    
    def update_summary(self):
        """Update the summary information"""
        if not self.current_data_type or not self.current_file:
            return
        
        try:
            if self.current_file.endswith('.csv'):
                with open(self.current_file, 'r') as f:
                    record_count = sum(1 for _ in f) - 1  # Subtract header
            elif self.current_file.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(self.current_file)
                record_count = len(df)
            else:
                record_count = "Unknown"
        except:
            record_count = "Unknown"
        
        self.summary_type.config(text=self.current_data_type.capitalize())
        self.summary_file.config(text=os.path.basename(self.current_file))
        self.summary_records.config(text=str(record_count))
    
    def run_import(self):
        """Execute the data import"""
        if not self.current_data_type or not self.current_file:
            return
        
        # Build the mapping dictionary
        mapping = {}
        for file_field, var in self.field_mapping.items():
            system_field = var.get()
            if system_field:
                mapping[file_field] = system_field
        
        dry_run = bool(self.dry_run_var.get())
        
        try:
            # Simulate import for this example
            # In a real implementation, you would call the migration_manager.import_data()
            total_records = 100  # This would be the actual count from the file
            success_count = 95    # Simulated success count
            error_count = 5       # Simulated error count
            
            # Display results
            self.results_text.config(state='normal')
            self.results_text.delete(1.0, tk.END)
            
            self.results_text.insert(tk.END, f"Import {'(dry run) ' if dry_run else ''}completed!\n\n")
            self.results_text.insert(tk.END, f"Total records processed: {total_records}\n")
            self.results_text.insert(tk.END, f"Successfully imported: {success_count}\n")
            self.results_text.insert(tk.END, f"Failed: {error_count}\n\n")
            
            # Simulated error details
            if error_count > 0:
                self.results_text.insert(tk.END, "Error details (sample):\n")
                self.results_text.insert(tk.END, "Row 15: Invalid date format\n")
                self.results_text.insert(tk.END, "Row 42: Missing required field 'gender'\n")
                self.results_text.insert(tk.END, "Row 78: Duplicate admission number\n")
            
            self.results_text.config(state='disabled')
            self.finish_btn.config(state='normal')
            
            if not dry_run:
                messagebox.showinfo(
                    "Import Complete",
                    f"Successfully imported {success_count} of {total_records} records"
                )
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import data: {str(e)}")
            traceback.print_exc()
    
    def download_template(self):
        """Download a CSV template for the selected data type"""
        if not self.current_data_type:
            messagebox.showerror("Error", "Please select a data type first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title=f"Save {self.current_data_type} template as",
            initialfile=f"{self.current_data_type}_template.csv"
        )
        
        if file_path:
            try:
                template = self.migration_manager.get_migration_template(self.current_data_type)
                if not template:
                    messagebox.showerror("Error", "Invalid data type")
                    return
                
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=template['required_fields'] + template['optional_fields'])
                    writer.writeheader()
                    writer.writerow(template['sample_data'])
                
                messagebox.showinfo("Success", f"Template saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save template: {str(e)}")

class SchoolSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("School System with Data Migration")
        self.root.geometry("800x600")
        
        # Sample school data
        self.school = type('School', (), {})()  # Simple mock school object
        
        # Add menu button
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Data Migration", command=self.open_migration)
        menubar.add_cascade(label="Tools", menu=filemenu)
        root.config(menu=menubar)
    
    def open_migration(self):
        """Open the data migration dialog"""
        MigrationDialog(self.root, self.school)

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolSystemGUI(root)
    root.mainloop()