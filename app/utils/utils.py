from app import db

def save(target):

    db.session.add(target)
    db.session.commit()

def delete(target):

    db.session.delete(target)
    db.session.commit()

def is_not_empty(*args):

    return all(len(value)> 0 for value in args)
