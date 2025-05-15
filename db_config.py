import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='pet_grooming_db'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None

def create_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS pet_grooming_db")
        cursor.execute("USE pet_grooming_db")
        
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create pets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                name VARCHAR(100) NOT NULL,
                breed VARCHAR(100),
                age INT,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Create services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
        """)
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                pet_id INT,
                booking_date DATETIME NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (pet_id) REFERENCES pets(id)
            )
        """)
        
        # Create booking_services table (for many-to-many relationship)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking_services (
                booking_id INT,
                service_id INT,
                price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (booking_id) REFERENCES bookings(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        """)
        
        # Insert default services if they don't exist
        services = [
            ('Nail Trim and Filing', 75),
            ('Teeth Brushing', 75),
            ('Eye Wash', 75),
            ('Ear Cleaning', 75),
            ('Frontline Application', 75),
            ('Anal Drain', 150),
            ('Facial Trimming', 150),
            ('Paw Shaving / Poodle Foot', 150),
            ('Butt & Belly Shaving', 150),
            ('Dematting (Small Breed)', 200),
            ('Dematting (Medium Breed)', 300),
            ('Dematting (Large Breed)', 400),
            ('Dematting (X-Large Breed)', 500)
        ]
        
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO services (name, price)
                VALUES (%s, %s)
            """, services)
        
        connection.commit()
        print("Database and tables created successfully")
        
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database() 