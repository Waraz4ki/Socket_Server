def compareObjectNameToString(iterable:list, name:str):
    """
    Returns the object in the list that equals the name if one exists, else it returns False
    """
    if not isinstance(iterable, list):
        raise TypeError("iterable is not a iterable")
    # loop through a list of objects
    for i in iterable:
        #check if objectName == name
        if i.__name__ == name:
            return i
    
    return None