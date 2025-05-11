Virtual environment set up with `uv` (to set up a virtual environment and run type `uv run flask run`), but the only dependency is `flask`, so `python -m flask run` works for now.

To access the dashboard create an user and log in. The 4 character 'E-Mail confirmation code' can be found on the console or in the corresponding entry in `db.csv`.

# Features
## Registration Page
- E-Mail address format validation using browser rules and a (**not** RFC5322 compliant) regex rule.
- Password strength validation, again with a simple regex rule.
- - 8 characters, one lower, one uppercase char and one digit is required.
- Phone number validation, again, regex.
- Address input, can accept special characters (including commas) and spaces except '|'.
- Error reporting.
- Passwords are salted and hashed using PKCSv2.

## E-Mail Confirmation Mockup
- Creates a random code and prints to console, the code can be found in the .csv file too.
- User can request new codes.
- 30 minute code timeout.

## Login Page
- Client side email validation.
- E-Mail and password pair checking.
- Sessions implementation.

## Dashboard
- Individual user listings.
- Pagination and support for variable number of entries per page* (see [dashboard.py](./app/routes/dashboard.py) ln. 15)
