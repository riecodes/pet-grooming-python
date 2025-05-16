# PetBuddy Grooming Services System

A Python-based pet grooming services management system with a Tkinter GUI, MySQL database integration, and PDF receipt generation.

## Features

- Customer and pet information management
- Service selection with dynamic pricing
- MySQL database integration for data persistence
- PDF receipt generation
- Modern and user-friendly interface

## Prerequisites

1. Python 3.7 or higher
2. XAMPP (for MySQL database)
3. Required Python packages (listed in requirements.txt)

## Installation

1. Clone or download this repository
   ```bash
   git clone https://github.com/riecodes/pet-grooming-python.git
   cd file-sharing-app
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start XAMPP and ensure MySQL service is running
4. Run the database setup script:
   ```bash
   python db_config.py
   ```

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. The main window will open with the following sections:
   - Customer Information
   - Pet Information
   - Available Services
   - Total and Action Buttons

3. To create a new booking:
   - Fill in customer and pet information
   - Select services from the list
   - Click "Save Booking" to store the information
   - Click "Generate Receipt" to create a PDF receipt

## Database Structure

The system uses the following tables:
- customers: Stores customer information
- pets: Stores pet information
- services: Contains available grooming services and prices
- bookings: Records booking information
- booking_services: Links bookings with selected services

## Receipt Generation

Receipts are generated as PDF files and stored in the `receipts` directory. Each receipt includes:
- Customer name
- Date and time
- List of services with prices
- Total amount
- Shop information

## Support

For any issues or questions, please create an issue in the repository. 