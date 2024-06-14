from bot.db.models.users import Users
from bot.db.schemas.users import Users as UsersDB
from sqlalchemy.orm import sessionmaker
from bot.db.db import engine


def add_user(user: Users):
    session = sessionmaker(engine)()
    user_db = UsersDB(user_id=user.user_id, username=user.username, status=user.status, days=user.days,
                      trial_status=user.trial_status)
    session.add(user_db) if not get_user(user.user_id) else ...
    session.commit()


def get_user(user_id: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    if not query:
        return False
    return query


def get_user_status(user_id: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    print(query)
    return query.status


def get_user_days(user_id: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    return int(query.days)


def change_status(user_id: int, new_status: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    query.status = new_status
    session.commit()


def change_days(user_id: int, days: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    query.days = days
    session.commit()


def get_all_users():
    session = sessionmaker(engine)()
    query = session.query(UsersDB).all()
    return query


def minus_day():
    session = sessionmaker(engine)()
    users = session.query(UsersDB).all()
    for user in users:
        if user.status == 1:
            days = user.days
            days -= 1
            user.days = days
    session.commit()


def get_user_trial(user_id: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    return query.trial_status


def change_trial(user_id: int, trial_status: int):
    session = sessionmaker(engine)()
    query = session.query(UsersDB).filter_by(user_id=user_id).first()
    query.trial_status = trial_status
    session.commit()
