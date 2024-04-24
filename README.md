# Fixit Backend

## Overview

Fixit is your go-to app for booking skilled handymen and household services, providing a wide array of professional service options at your fingertips.

### Links to Related Repositories:

- Fixit Users frontend: [https://github.com/fixit-pesce/users-fixit-frontend-new](https://github.com/fixit-pesce/users-fixit-frontend-new)

- Fixit Service Providers frontend: [https://github.com/fixit-pesce/sp-fixit-frontend](https://github.com/fixit-pesce/sp-fixit-frontend)

- Fixit Admin frontend: [https://github.com/fixit-pesce/admins-fixit-frontend](https://github.com/fixit-pesce/admins-fixit-frontend)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/fixit-pesce/fixit-backend-new.git
   ```

2. **Navigate to the project directory**

   ```bash
   cd fixit-backend-new
   ```
   
3. **Install dependencies using a virtual environment:**

   a. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
   
   b. Activate the virtual environment:
     - **Linux/macOS:**
       ```bash
       source venv/bin/activate
       ```
     - **Windows:**
       ```bash
       venv\Scripts\activate
       ```
   c. Install the required dependencies:
      ```bash
      pip install -r requirements.txt
      ```


## Run the backend server

1. Start the server using Uvicorn:
```bash
uvicorn app.main:app --reload
```

## API Documentation

The API documentation can be accessed at: `http://localhost:8000/docs`
