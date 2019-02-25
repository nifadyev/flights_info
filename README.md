# Flights informer

# TODO:
 - Add input args (from(IATA code), where(IATA code), date(dd.mm.yyyy), return date (optional))
 - Papse input args
 - Add exception handler
 - Add unit tests (or doctests)
 - Output info to console (if info about flight exists)
    - Accurate time of departure and arriving
    - Flight time
    - Sort by price
    - Final price of 2 way flights 
 - Use pylint and flake8 for linting

# App structure
1. Pass sys args to main func (find_flights_info)
2. Inside this func parse this args
3. If they are invalid, raise an exception, with suggestion to correct invalid arg(s)
4. Check other args
    1. Check dates (is it correct string, is there any flights for these date)
    2. Check route (is this route available)
    3. Check city codes (probably extra)
    4. If any of args is invalid, throw an exception and guiding message
5. Create url for request
6. Exec get request
7. Get path to content table
8. Print information
    1.Calc flight duration
    2. Output would differ depending on whether its return flight or not