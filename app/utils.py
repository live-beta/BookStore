from app import db

def save(target):
    """" Simplification function for database save operaions """

    db.session.add(target)
    db.session.commit()

def delete(target):
    """ function to simplify delete database delete functions"""

    db.session.delete(target)
    db.session.commit()

def is_not_empty(*args):
    """Checking none empty passes functions """
    return all(len(value)> 0 for value in args)
