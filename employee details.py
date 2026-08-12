'''emp id, name, designation department and salary of 5 ppl through json in table'''
import json
import os

def get_file_path():
    return os.path.join(os.path.dirname(__file__), 'emp_details.json')

def add_employee():
    try:
        emp_id = int(input("Enter Emp ID: "))
        emp_name = input("Enter Name: ")
        designation = input("Enter Designation: ")
        department = input("Enter Department: ")
        salary = int(input("Enter Salary: "))
    except ValueError:
        print("Invalid input for ID or Salary. They must be numbers.")
        return

    new_emp = {
        "emp_id": emp_id,
        "emp_name": emp_name,
        "Designation": designation,
        "Department": department,
        "Salary": salary
    }
    
    file_path = get_file_path()
    
    # Load existing data
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                emp_data = json.load(file)
            except json.JSONDecodeError:
                emp_data = []
    else:
        emp_data = []
        
    # Append new employee
    emp_data.append(new_emp)
    
    # Save back to JSON
    with open(file_path, 'w') as file:
        json.dump(emp_data, file, indent=2)
    print("Employee added successfully!\n")

def display_employee_table():
    file_path = get_file_path()
    if not os.path.exists(file_path):
        print("No employee data found.")
        return
        
    with open(file_path, 'r') as file:
        try:
            emp_data = json.load(file)
        except json.JSONDecodeError:
            print("Error reading JSON data.")
            return
            
    print(f"\n{'Emp ID':<10} | {'Name':<15} | {'Designation':<15} | {'Department':<15} | {'Salary':<10}")
    print("-" * 75)
    for emp in emp_data:
        print(f"{emp.get('emp_id', ''):<10} | {emp.get('emp_name', ''):<15} | {emp.get('Designation', ''):<15} | {emp.get('Department', ''):<15} | {emp.get('Salary', ''):<10}")
    print()

if __name__ == "__main__":
    while True:
        print("1. Add New Employee")
        print("2. Display Employees")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            add_employee()
        elif choice == '2':
            display_employee_table()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.\n")
