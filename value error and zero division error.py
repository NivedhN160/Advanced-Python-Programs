#catch value error and zero division error
try:
    a = int(input("enter value of a: "))
    b = int(input("enter value of b: "))
    c = a / b
    print("A/B = ", c)
except ValueError:
    print("Error: Please enter valid integer values.")
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")