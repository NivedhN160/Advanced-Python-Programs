import json
student_json='{"name":"Ravi", "age":21, "marks":88}'
student=json.loads(student_json)
print(student['name'])
print(student['marks'])