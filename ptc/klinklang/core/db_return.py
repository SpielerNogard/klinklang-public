def db_return(result):
    """
    Method to convert a MongoDB result to a list of dictionaries without the _id field
    """
    return [
        {key: value for key, value in item.items() if key not in ["_id"]}
        for item in result
    ]
