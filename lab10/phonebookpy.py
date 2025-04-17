import psycopg2
import csv

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '12070107Don',
    'host': 'localhost',
    'port': '5432'
}


def add_user(name, number):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO phone_book(name, number) 
            VALUES (%s, %s)
            """,
            [name, number]
        )
        conn.commit()
        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


# IF FLAG == 1 (UPDATE BY NAME), FLAG == 0 THEN BY NUMBER
def update(name, number, flag):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if flag == 1:
            cursor.execute(
                """
                UPDATE phone_book
                SET number = %s WHERE name = %s
                """,
                [number, name]
            )
            conn.commit()
            return True

        elif flag == 0:
            if flag == 1:
                cursor.execute(
                    """
                    UPDATE phone_book
                    SET name = %s WHERE number = %s
                    """,
                    [name, number]
                )
                conn.commit()
                return True


    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


def delete_by_username(name):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM phone_book
            WHERE name = %s
            """,
            [name]
        )
        conn.commit()
        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


def search(name, number):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM phone_book
            WHERE name = %s OR number = %s
            """,
            [name, number]
        )
        conn.commit()
        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def input_csv():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        with open('book1.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Skip header row
            for row in reader:
                cursor.execute(
                    "INSERT INTO phone_book (number, name) VALUES (%s, %s)",
                    (row[0], row[1].strip())
                )
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()



if __name__ == '__main__':
    add_user("vova",77750712929)
    add_user("vlad",77017875535)

    update("vlad",700000,1)
    delete_by_username("vlad")

    update("new_vova",77750712929,0)

    search("new_vova",1)
    input_csv()


