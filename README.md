# Recitation Scheduler
## João de Araujo Junior

Recitation Scheduler is a csv file parser that matches students and TAs based on their time availabilities to schedule their recitations. 

### Google form formatting

In order for the program to correctly parse the csv files, the google forms must contains two questions with the following titles (not case sensitive):

* Name 
* Availability

Questions with different titles are ignored and the order of the questions does not matter. Different questions with these two headers should also be avoided.

#### Students' form

The students' form should contain these question types:

* Short answer 
* Checkbox

The short answer is intended for the students' names. The checkbox is used by the students to select their availability. In order for the time slots in the form to match the regex used by the parser, the time slots must be formatted like explained below.

##### Time slot formatting

* Days of the week must be the first three letters of their names (case sensitive), i.e. `Sun, Mon, Tue, Wed, Thu, Fri, Sat`.
* Times of day should either be in a 12-hour or 24-hour format with a colon in between the hour and minute digits and a hyphen between the start and end times (if am and pm is not used, the time will be assumed to be in the 24-hour format), e.g. `3:30pm-4:30pm` or `17:00-18:00`. Note: 12-hour times should not contain a leading 0, meaning `03:30pm-04:30pm` will not be accepted by the regex. The 24-hour times can have a leading 0, however, this time format must remain consistent between the student and TA forms. 
* The day and time of day in each option of the checkbox should be separated by a space, e.g. `Wed 3:30pm-4:30pm` or `Fri 10:00-11:00`.

##### Image example

![Short answer "Name" question](images/Screenshot%20(15).png)

![Checkbox "Availability" question](images/Screenshot%20(16).png)

#### TAs' form

The TAs' form should contain these question types:

* Short answer 
* Checkbox grid

The short answer is intended for the TAs' names. The checkbox is by the TAs to select their availability. In order for the time slots in the form to match the regex used by the parser, the time slots must be formatted like explained below.

##### Time slot formatting

* Days of the week must be the first three letters of their names (case sensitive), i.e. `Sun, Mon, Tue, Wed, Thu, Fri, Sat`.
* Times of day should either be in a 12-hour or 24-hour format with a colon in between the hour and minute digits and a hyphen between the start and end times (if am and pm is not used, the time will be assumed to be in the 24-hour format), e.g. `3:30pm-4:30pm` or `17:00-18:00`. Note: 12-hour times should not contain a leading 0, meaning `03:30pm-04:30pm` will not be accepted by the regex. The 24-hour times can have a leading 0, however, this time format must remain consistent between the student and TA forms. 
* The columns of the checkbox grid should be days of the week, e.g. `Wed, Fri, Sun`. The rows of the checkbox grid should be time slots, e.g. `6:00pm-7:00pm` or `01:00-02:00`. 

##### Image example

![Short answer "Name" question](images/Screenshot%20(17).png)

![Checkbox grid "Availability" question](images/Screenshot%20(18).png)

### Usage

```
py or python3 recitation_scheduler_V3.py [csv]
```

Where `csv`, when typed as an argument, signals to the parser to output a file named scheduleAssignment.csv with the students and time slots assigned to each TA in csv format. 

If the argument `csv`is not used, then each TA's assignment will just be printed out to the terminal. 

Once the program executes, it will ask for the paths of the time availability .csv files for the TAs and students. These can be absolute or relative paths. 
```
Input the file path of the .csv file with TA time slot
>
Input the file path of the .csv file with Student time slots
>
```

### Testing

There are two unit test functions `unit_test_model()` and `unit_test_large_data()` available. The former tests the basic mixed-integer linear programming model with a small data set. The latter uses a data set representative of what will be used in real life with students and TAs and also tests the csv parsing capabilities of the program. 