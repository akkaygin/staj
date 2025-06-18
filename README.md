Virtual environment set up with `uv` (to set up a virtual environment and run type `uv run flask run`).

To access the dashboard create an user and log in. The 4 character 'E-Mail confirmation code' can be found on the console.

# Features
## SQL Backend
- Uses sqlite3 for database operations. Does not depend on sqlalchemy.

## Registration Page
- E-Mail address format validation using browser rules and a (**not** RFC5322 compliant) regex rule.
- Password strength validation, again with a simple regex rule.
- - 8 characters, one lower, one uppercase char and one digit is required.
- Phone number validation, again, regex.
- Address input, can accept special characters.
- Error reporting.
- Passwords are salted and hashed using PKCSv2.

## E-Mail Confirmation Mockup
- Creates a random code and prints to console, the code can be found in the dashboard too.
- User can request new codes.
- 30 minute code timeout.

## Login Page
- Client side email validation.
- E-Mail and password pair checking.
- Session management with Flask-Login.

## Dashboard
- Table display with sorting options.
- Pagination and support for variable number of entries per page.