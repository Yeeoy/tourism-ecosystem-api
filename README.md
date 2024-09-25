
## Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/Yeeoy/tourism-ecosystem-api.git

   cd tourism-ecosystem-api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Perform database migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

You can now access the project at http://localhost:8000.



## Usage Guide

### Admin Backend

The admin interface can be accessed at:
http://localhost:8000/admin

Admin login credentials:
- Username: admin@uow.com
- Password: uowadmin

### API Endpoints

Our project provides the following main API endpoints:

- `/api/customUser/`: User-related operations
- `/api/accommodation/`: Accommodation management
- `/api/events/`: Event organizer operations
- `/api/transport-services/`: Local transportation services
- `/api/dining/`: Restaurant and café related operations
- `/api/tourism-info/`: Tourism information center services

For detailed API documentation and interactive testing, visit:
- API Schema: `/api/schema/`
- Swagger UI: `/api/docs/` or the root URL `/`


