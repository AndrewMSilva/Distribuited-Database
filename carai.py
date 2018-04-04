from pyparsing import Regex, QuotedString, delimitedList

# Object names and numbers match these regular expression
object_name = Regex('[a-zA-Z_]+')
number = Regex('-?[0-9]+')
# A string is just something with quotes around it - PyParsing has a built in
string = QuotedString("'") | QuotedString('"')

# A term is a number or a string
term = number | string

# The values we want to capture are either delimited lists of expressions we know about...
column_list = (delimitedList(object_name)).setResultsName('columns')
term_list = (delimitedList(term)).setResultsName('terms')

# Or just an expression we know about by itself
table_name = object_name.setResultsName('table')

# And an SQL statement is just all of these pieces joined together with some string between them
sql_stmt = "insert into " + table_name + "(" + term_list + ");"


if __name__ == '__main__':
    res = sql_stmt.parseString("""insert into cliente('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam sodales non metus sit amet condimentum. Phasellus sed nisi eu magna blandit feugiat in et nulla. Nunc tempus nunc convallis, ultrices ipsum in, eleifend orci. Phasellus nec leo augue. Etiam amet. ', 8, 'que');""")
    print(res.table)         # ref_geographic_region
    print(list(res.columns)) # ['continent_id', 'name']
    print(list(res.terms))   # ['8', 'Europe (Western)']
