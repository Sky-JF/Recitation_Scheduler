import pulp
import csv
from os import path
import re
import sys

"""
PineCode Recitation Scheduling Challenge
João de Araujo Junior
阮

To write a .csv file with the time slot and students assignments for each TA, use the argument "csv" when executing the file

This project uses mixed-integer linear programming to find an optimal pairing of students and tas with available time slots

Check the PineCode shared drive for the expected .csv format from google forms
Note: time slot availabilities must match the regex below
Assumption: The time slots students filled in must be a subset of the available time slots for TAs
"""

# regex patter to validate dictionary values for time slots available to each person
pattern_TA_header = re.compile(
  r"^availability \[" 
  r"(([1-9]|1[0-2]):([0-5][0-9])(am|pm)?|"
  r"([01]?[0-9]|2[0-3]):([0-5][0-9]))-"
  r"(([1-9]|1[0-2]):([0-5][0-9])(am|pm)?|"
  r"([01]?[0-9]|2[0-3]):([0-5][0-9]))"
  r"\]$"
)

wrong_patter_TA_header = re.compile(
  r"^availability.*$"
)

pattern_TA_days = re.compile(
  r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$"
)

pattern_student = re.compile(
  r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) "
  r"(([1-9]|1[0-2]):([0-5][0-9])(am|pm)?|"
  r"([01]?[0-9]|2[0-3]):([0-5][0-9]))-"
  r"(([1-9]|1[0-2]):([0-5][0-9])(am|pm)?|"
  r"([01]?[0-9]|2[0-3]):([0-5][0-9]))$"
)

def main():
  use_csv = False
  if len(sys.argv) > 1 and sys.argv[1] == "csv":
    use_csv = True

  file_student, file_ta = get_csv_file()
  students, tas, slots, student_avail, ta_avail, ta_id, student_id = process_csv_file(file_student, file_ta)
  x, y = create_LP_model(students, tas, slots, student_avail, ta_avail)
  plotResults(x, y, students, tas, slots, student_id, ta_id, use_csv)

def get_csv_file():
  """
  Get the absolute file path of the files with the student and ta data from the google form

  return: 
    absolute file path string of each file: file_name_student, file_name_ta
  """

  print("Input the file path of the .csv file with TA time slots")
  csv_file_ta = input("> ")
  csv_file_ta = csv_file_ta.strip("\"")
  file_name_ta = path.abspath(csv_file_ta)
  print("Input the file path of the .csv file with Student time slots")
  csv_file_student = input("> ")
  csv_file_student = csv_file_student.strip("\"")
  file_name_student = path.abspath(csv_file_student)

  return file_name_student, file_name_ta

def process_csv_file(file_name_student, file_name_ta):
  """
  Process the two .csv files inputted by the user in the command line to list TAs and students

  input:
    absolute file path of the csv file with the student data file_name_student
    absolute file path of the csv file with the ta data file_name_ta

  return:
    List students with the IDs of the students to be assigned
    List tas with the IDs of the TAs to be assigned
    List slots with the strings of the time availabilities
    Dict student_avail mapping the ID of a student to a set of their available slots
    Dict ta_avail mapping the ID of a TA to a set of their available slots
    Dict taID mapping the id of a TA to their name
    Dict studentID mapping the id of a student to their name
  """

  students, tas, slots = [], [], []
  student_avail, ta_avail = {}, {}
  ta_id, student_id = {}, {}

  seen_slots = set()

  with open(file_name_ta, 'r') as file:
    reader = csv.DictReader(file)
    curr_id = 0
    for row in reader: # 1 row per person
      for key in row: # 1 key per question in the google form
        if key.lower() == 'name':
          ta_id[curr_id] = row[key]
          tas.append(curr_id)
          ta_avail[curr_id] = set()
        elif bool(pattern_TA_header.match(key.lower())) and len(row[key]) > 2: #check this is not an empty value
          days = row[key].split(';')
          time = key[key.find("[")+1:key.find("]")] #exclude brackets, only include inside
          time = time.strip() 
          for day in days:
            day = day.strip()
            if bool(pattern_TA_days.match(day)):
              new_val = day + " " + time
              ta_avail[curr_id].add(new_val)
              if new_val not in seen_slots:
                slots.append(new_val)
                seen_slots.add(new_val)
            else:
              print("Invalid regex: ", day)
        elif not bool(pattern_TA_header.match(key.lower())) and bool(wrong_patter_TA_header.match(key.lower())):
          print("Invalid regex: ", key)
      curr_id += 1

  with open(file_name_student,'r') as file:
    reader = csv.DictReader(file)
    curr_id = 0
    for row in reader: # 1 row per person
      for key in row: # 1 key per survey question
        if key.lower() == 'name':
          student_id[curr_id] = row[key]
          students.append(curr_id)
          student_avail[curr_id] = set()
        elif key.lower() == 'availability':
          times = row[key].split(';')
          for time in times:
            time = time.strip()
            if bool(pattern_student.match(time)): #check if the time availability entry matches the regex
              student_avail[curr_id].add(time)
              if time not in seen_slots:
                slots.append(time)
                seen_slots.add(time)
            else:
              print("Invalid regex: ", time)
      curr_id += 1
  
  return students, tas, slots, student_avail, ta_avail, ta_id, student_id

def create_LP_model(students, tas, slots, student_avail, ta_avail):
  """
  Create and solve a mixed-integer linear programming model to find the optimal time slot assignments
  for TAs and students

  input:
    list students and tas with the IDs of each 
    list slots with the time slots available for choosing
    dict student_avail and ta_avail with a set of availabilities of each student and TA
  
  return:
    linear programming variable x (dictionary) mapping a student to a TA and time slot (student -> ta -> slot)
    linear programming variable y (dictionary) mapping a TA to a time slot (ta -> slot)
    Note: in both x and y, must look through all values in the dictionary to find combinations that result in 1
    due to how the LP problem is set up 
  """
  model = pulp.LpProblem("TA_Assignment", pulp.LpMaximize)

  x = pulp.LpVariable.dicts("x", (students, tas, slots), cat="Binary")
  y = pulp.LpVariable.dicts("y", (tas, slots), cat="Binary")

  max_students_per_TA = pulp.LpVariable("MaxStudentsPerTA", lowBound=0, cat="Integer")
  # This variable is used to incentivize the model to distribute students assigned to the same time slot between TAs

  # Objective: maximize number of students assigned
  model += pulp.lpSum(x[s][t][h] for s in students for t in tas for h in slots) - 0.01 * max_students_per_TA

  # Constraint: each TA cannot exceed max_students_per_TA
  for t in tas:
    model += pulp.lpSum(x[s][t][h] for s in students for h in slots) <= max_students_per_TA

  # Constraint: a student can only be assigned to one time slot & TA
  for s in students:
    model += pulp.lpSum(x[s][t][h] for t in tas for h in slots) <= 1

  # Constraint: the student must be available in their chosen time slot
  for s in students:
    for t in tas:
      for h in slots:
        if h not in student_avail[s] or h not in ta_avail[t]:
          model += x[s][t][h] == 0

  # Constraint: Distribute students to a TA in the same time slot
  # This part is necessary to assure a student is assigned to a time slot a TA made available
  for t in tas:
    for h in slots:
      model += pulp.lpSum(x[s][t][h] for s in students) <= len(students) * y[t][h]

  # Constraint: TA can only host one time slot
  for t in tas:
    model += pulp.lpSum(y[t][h] for h in slots) <= 1

  model.solve(pulp.PULP_CBC_CMD(msg=False))
  print("Status:", pulp.LpStatus[model.status])

  return x, y

def plotResults(x, y, students, tas, slots, student_id, ta_id, write_csv=False):
  """
  Print the resulting assignments for each TA. If specified, write to a csv file. 

  Input: 
  x linear programming variable student -> ta -> slot mapping to the optimal choice for each student (must be == 1)
  y linear programming variable ta -> slot mapping to the optimal choice for each ta (must be == 1)
  students, tas lists with the IDs of each
  slots list with the strings of the time slots
  Dict mapping ids to names: studentID, taID 
  """
  if(write_csv):
    write_csv_file(x, y, students, tas, slots, student_id, ta_id)

  has_schedule = set()

  print("\nAssignments:")
  for t in tas:
    for h in slots:
      if pulp.value(y[t][h]) == 1: #if the ta chose this time slot
        print(f"{ta_id[t]}: {h}")
        assigned = [s for s in students if pulp.value(x[s][t][h]) == 1]
        for s in assigned:
          print("|\n+--", student_id[s])
          has_schedule.add(s)
        print()
  
  first = True
  for s in students: #find students without a schedule
    if s not in has_schedule:
      if first:
        first= False
        print("Students missing assignments: ")
      else:
        print("|")
      print("+--", student_id[s])


def write_csv_file(x, y, students, tas, slots, student_id, ta_id):
  """
  Write the TA assignments to a csv file that can be uploaded to google sheets.

  Input:
  x linear programming variable student -> ta -> slot mapping to the optimal choice for each student (must be == 1)
  y linear programming variable ta -> slot mapping to the optimal choice for each ta (must be == 1)
  students, tas lists with the IDs of each
  slots list with the strings of the time slots
  Dict mapping ids to name, studentID, taID
  """
  has_schedule = set()

  data = []
  curr_data = 0

  for t in tas:
    for h in slots:
      if pulp.value(y[t][h]) == 1: #if the ta chose this time slot
        data.append({})
        data[curr_data]['name'] = ta_id[t]
        data[curr_data]['time'] = h
        assigned = [s for s in students if pulp.value(x[s][t][h]) == 1]
        data_students = ""
        first = True
        for s in assigned:
          if first:
            first = False
          else:
            data_students += ";"
          data_students += student_id[s]
          has_schedule.add(s)
        data[curr_data]['students'] = data_students
        curr_data += 1

  all_assigned = True
  data_students = ""
  for s in students: #find students without a schedule
    if s not in has_schedule:
      if all_assigned:
        data.append({})
        data[curr_data]['name'] = 'not assigned'
        data[curr_data]['time'] = ''
        all_assigned = False
        first = True
      if first:
        first = False
      else:
        data_students += ";"
      data_students += student_id[s]
  if not all_assigned:
    data[curr_data]['students'] = data_students

  with open('recitation_assignments.csv', 'w', newline='') as csvFile:
    fieldnames = ['name', 'time', 'students']
    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

def unit_test_model():
  """
  Unit test of the mixed-integer linear programming model with small amount of data
  """
  students = ["S1", "S2", "S3", "S4", "S5"]
  tas = ["TA1", "TA2"]
  slots = ["MonAM", "MonPM", "TueAM"]

  student_avail = {
    "S1": {"MonAM", "MonPM"},
    "S2": {"MonAM", "TueAM"},
    "S3": {"MonPM"},
    "S4": {"TueAM"},
    "S5": {"TueAM"}
  }

  ta_avail = {
    "TA1": {"MonAM", "TueAM"},
    "TA2": {"MonPM"}
  }

  x, y = create_LP_model(students, tas, slots, student_avail, ta_avail)

  for t in tas:
    for h in slots:
      if pulp.value(y[t][h]) == 1:
        assigned = [s for s in students if pulp.value(x[s][t][h]) == 1]
        print(f"{t} hosts at {h} with students {assigned}")

def unit_test_large_data():
  """
  Integration test of the whole architecture with the large data set
  """
  use_csv = True
  rel_path_student = "./Recitation Scheduling Example - Student.csv"
  rel_path_ta = "./Recitation Scheduling Example - TA.csv"
  file_student = path.abspath(rel_path_student)
  file_ta = path.abspath(rel_path_ta)
  students, tas, slots, student_avail, ta_avail, ta_id, student_id = process_csv_file(file_student, file_ta)
  x, y = create_LP_model(students, tas, slots, student_avail, ta_avail)
  plotResults(x, y, students, tas, slots, student_id, ta_id, use_csv)

if __name__ == "__main__":
  main()