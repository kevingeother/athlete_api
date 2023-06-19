"""
Helper functions
"""

from typing import List

from sqlmodel import column, func
from sqlmodel.sql.expression import Select


def verify_params(noc: str, sport: str, start_date: int,  end_date: int):
    """
     Verify parameters for return message / error. This is a helper function to make sure all required parameters are present
     
     Args:
     	 noc: NoC string ( required )
     	 sport: Service port string ( required ) 
     	 start_date: Start date of period ( required )
     	 end_date: End date of period ( required )
     
     Returns: 
     	 True if everything is fine else raise exception to indicate why it is not possible to get data from API
    """
    # Path parameter is mandatory.
    if not noc:
        raise ValueError("Path parameter is mandatory")
    # At least one query parameter is mandatory
    if not sport and not (start_date or end_date):
        raise ValueError("At least one query parameter is mandatory")
    # Check if start and end dates are both true or false
    if  bool(start_date) ^ bool(end_date):
        raise ValueError("Both start and end dates needed for period")
    # Check data validity
    elif start_date and end_date and start_date > end_date:
        raise ValueError("Start date should be less than end date")
    return True

def add_where(statement:Select, clauses:List):
    """
     Add where clauses to select statement. This is a helper function to make it easier to add clauses to select statements
     
     Args:
     	 statement: select statement to add clauses to
     	 clauses: list of tuples ( attr value relation )
     
     Returns: 
     	 statement with clauses added to it 
    """
    for (attr, value, relation) in clauses:
        print(attr, value, relation)
        #add assertion
        # attr:str, value:str|int|float, relation:str = 'equal'):

        # Skips if the relation is non_null and value is None.
        if relation!='non_null' and not value:
            continue

        # Returns a SQL statement to select a relation
        # This if else ladder is used to build the SQL statement for the relation.
        if isinstance(value, str):
            if relation=='equal':
                statement = statement.where(func.lower(column(attr))==value.lower())
            elif relation=='contain':
                statement = statement.where(func.lower(column(attr)).contains(value.lower()))
            elif relation=='non_null':
                statement = statement.where(func.lower(column(attr)) is not None)
        elif isinstance(value, (int, float)):
            if relation=='equal':
                statement = statement.where(column(attr)==value)
            elif relation=='unequal':
                statement = statement.where(column(attr)!=value)
            elif relation=='non_null':
                statement = statement.where(column(attr) is not None)
            elif relation=='gt':
                statement = statement.where(column(attr)>value)
            elif relation=='gte':
                statement = statement.where(column(attr)>=value)
            elif relation=='lt':
                statement = statement.where(column(attr)<value)
            elif relation=='lte':
                statement = statement.where(column(attr)<=value)
        elif isinstance(value, bool):
            if relation=='equal':
                statement = statement.where(column(attr)==value)
            elif relation=='unequal':
                statement = statement.where(column(attr)!=value)
            elif relation=='non_null':
                statement = statement.where(column(attr) is not None)

    return statement

#TODO better looks as class
# class Statement(Select):
#     def __init__(self) -> None:
#         super().__init__()

#     def add_where(self, attr:str, value:str|int|float, relation:str = 'equal'):
#         if not value:
#             return self

#         if isinstance(value, str):
#             if relation=='equal':
#                 self = self.where(func.lower(text(attr)) == value.lower())
#                 self.
#             elif relation=='contain':
#                 self = self.where(func.lower(text(attr)).contains(value.lower()))
#         elif isinstance(value, (int, float)):
#             if relation=='equal':
#                 self = self.where(text(attr)==value)
#             elif relation=='unequal':
#                 self = self.where(text(attr)!=value)
#             elif relation=='gt':
#                 self = self.where(text(attr)>value)
#             elif relation=='gte':
#                 self = self.where(text(attr)>=value)
#             elif relation=='lt':
#                 self = self.where(text(attr)<value)
#             elif relation=='lte':
#                 self = self.where(text(attr)<=value)
    
