import psycopg

#this creates the database if it doesn't exist
def create_database(dbname, user, password, host, port):
    try:
        conn = psycopg.connect(dbname="postgres", 
                               user=user, 
                               password=password, 
                               host=host, 
                               port=port)

        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {dbname.lower()}")
        print(f"Database {dbname} created successfully.")
    except psycopg.errors.DuplicateDatabase:
        print(f"Database {dbname} already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
    finally:
        cur.close()
        conn.close()

#this connects the program to the database
def connectToDataBase():
    dbname = "student".lower()
    #the following should be your password and username to the database.
    user = "your username"
    password = "your password"
    host = "localhost"
    port = "5432"

    try:
        conn = psycopg.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        print("Connecting to the database...")
        return conn
    except psycopg.OperationalError as e:
        if "does not exist" in str(e).lower():
            print("Database does not exist. Creating database...")
            create_database(dbname, user, password, host, port)

            try:
                conn = psycopg.connect(dbname=dbname, user=user, password=password, host=host, port=port)
                print("Connection successful.")
                return conn
            except Exception as e:
                print(f"Failed to connect after creation: {e}")
                exit(1)

        else:
            print(f"Error: {e}")
            exit(1)

#this creates the table, if it doesn't exist.
def createTable(conn):
    cursor = conn.cursor()
    createTableSql = '''
    CREATE TABLE IF NOT EXISTS students (
        student_id SERIAL PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        enrollment_date DATE
    );
    '''

    try:
        cursor.execute(createTableSql)
        conn.commit()
        print("Table created successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()

#this initialize the data.
def initialize_data(conn):
    cursor = conn.cursor()

    insertDataSql = '''
    INSERT INTO students (first_name, last_name, email, enrollment_date) VALUES
    ('John', 'Doe', 'john.doe@example.com', '2023-09-01'),
    ('Jane', 'Smith', 'jane.smith@example.com', '2023-09-01'),
    ('Jim', 'Beam', 'jim.beam@example.com', '2023-09-02')
    ON CONFLICT (email) DO NOTHING;
    '''

    try:
        cursor.execute(insertDataSql)
        conn.commit()
        print("Initialized data successfully!")
        
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")
        conn.rollback()
    finally:
        cursor.close()

#this sends the query to database and ask for all student info.
def getAllStudents(conn):
    cursor = conn.cursor()
    query = 'SELECT * FROM students'
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n The query results:")
        for row in results:
            print(row)
        print()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

#this adds a new student to the database
def addStudent(conn, firstName, lastName, email, enrollmentDate):
    cursor = conn.cursor()
    sqlStatement = """
    INSERT INTO students (first_name, last_name, email, enrollment_date) 
    VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(sqlStatement, (firstName, lastName, email, enrollmentDate))
        conn.commit()
        print("New student added successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()

#this updates the student email with provided studentID and new email
def updateStudentEmail(conn, student_id, new_email):
    cursor = conn.cursor()
    try:
        sqlStatement = "UPDATE students SET email = %s WHERE student_id = %s;"
        cursor.execute(sqlStatement, (new_email, student_id))
        
        if cursor.rowcount == 0:
            print(f"No student found with ID {student_id}, or the email is already up to date.")
        else:
            conn.commit()
            print(f"Student ID {student_id}'s email updated to {new_email}.")
        
    except Exception as e:
        print(f"An error occurred while updating the email: {e}")
        conn.rollback()
    finally:
        cursor.close()

#this deletes the student with the provided studentID
def deleteStudent(conn, student_id):
    cursor = conn.cursor()
    try:
        sqlStatement = "DELETE FROM students WHERE student_id = %s;"
        cursor.execute(sqlStatement, (student_id,))
        
        if cursor.rowcount == 0:
            print(f"No student found with ID {student_id}, or they have already been deleted.")
        else:
            conn.commit()
            print(f"Student with ID {student_id} has been successfully deleted.")
        
    except Exception as e:
        print(f"An error occurred while deleting the student: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    conn = connectToDataBase()
    createTable(conn)
    initialize_data(conn)

    while True:
        print("\nPlease select your operation:")
        print("1. Get all the students from the database.")
        print('2. Add a student into the database.')
        print('3. Update the student email to the database')
        print('4. Delete a student from the database.')
        print('5. Exit the program.\n')

        while True:
            try:
                userInput = int(input('Please enter an integer:'))
                break;
            except ValueError as error:
                print("Please enter a correct integer!\n")

        if (userInput == 1):
            getAllStudents(conn)
        elif (userInput == 2):
            newStudentFirstName = input('Please input the student first name:')
            newStudentLastName = input('Please input the student last name:')
            newStudentEmail = input('Please enter new student email:')
            newStudentEnrollmentDate = input('Please enter new student enrollment date (year-month-date):')
            addStudent(conn, newStudentFirstName, newStudentLastName, newStudentEmail, newStudentEnrollmentDate)
        elif (userInput == 3):
            while True:
                try:
                    newStudentID = int(input('Please enter the student ID:'))
                    break;
                except ValueError as error:
                    print("Please enter a correct integer!\n")
            
            newEmail = input('Please enter the new student email:')
            updateStudentEmail(conn, newStudentID, newEmail)
            
        elif (userInput == 4):
            while True:
                try:
                    deleteItem = int(input('Please enter the studentID that you want to delete:'))
                    break;
                except ValueError as error:
                    print("Please enter a correct integer!\n")

            deleteStudent(conn, deleteItem)
            
        elif (userInput == 5):
            print('Exiting the program...')
            break


    conn.close()


main()
