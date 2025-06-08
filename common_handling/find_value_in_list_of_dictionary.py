def execute(search_key, search_value, dictionary):
    for object in dictionary:
        if object[search_key] == search_value:
            return object