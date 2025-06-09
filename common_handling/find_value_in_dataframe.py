def execute(data, search_value, reference_column, search_column = None):
    if search_column is None:
       return data[data[reference_column] == search_value]
    else:
       return data[data[reference_column] == search_value][search_column]