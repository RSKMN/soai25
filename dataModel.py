import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, UnicodeText, DateTime, ForeignKey, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.types import TypeDecorator

Base = declarative_base()

# Custom type decorator to store list as JSON string in TEXT column
class JSONEncodedList(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return '[]'
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        return json.loads(value)

# User model
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    display_name = Column(String(128), nullable=False)
    email = Column(String(128))
    submitted_proverbs = relationship('Proverb', back_populates='contributor')
    submitted_twisters = relationship('TongueTwister', back_populates='contributor')

# Proverb model
class Proverb(Base):
    __tablename__ = 'proverb'
    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText, nullable=False)  # Telugu Unicode text
    contributor_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    meaning = Column(UnicodeText)
    region = Column(String(128))
    tags = Column(JSONEncodedList())  # List of tags stored as JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)
    contributor = relationship('User', back_populates='submitted_proverbs')

# Tongue Twister model
class TongueTwister(Base):
    __tablename__ = 'tongue_twister'
    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText, nullable=False)
    contributor_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    region = Column(String(128))
    audio_url = Column(String(256))
    difficulty = Column(String(32))
    timestamp = Column(DateTime, default=datetime.utcnow)
    contributor = relationship('User', back_populates='submitted_twisters')

# Example usage: create database and add example records
if __name__ == '__main__':
    # Create SQLite engine (update with your database URI if needed)
    engine = create_engine('sqlite:///telugu_proverbs_twisters.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a user
    new_user = User(display_name='Ravi', email='ravi@example.com')
    session.add(new_user)
    session.commit()

    # Add a proverb
    new_proverb = Proverb(
        text='తెగిన వెన్న మీద ముసి దాలే లేదు',
        contributor_id=new_user.id,
        meaning='A broken backbone cannot carry burden',
        region='Andhra Pradesh',
        tags=['wisdom', 'life']
    )
    session.add(new_proverb)
    session.commit()

    # Add a tongue twister
    new_twister = TongueTwister(
        text='కారు కారు కారుమాటలు',
        contributor_id=new_user.id,
        region='Telangana',
        audio_url=None,
        difficulty='Medium'
    )
    session.add(new_twister)
    session.commit()

    # Query to verify entries
    user_proverbs = session.query(Proverb).filter_by(contributor_id=new_user.id).all()
    user_twisters = session.query(TongueTwister).filter_by(contributor_id=new_user.id).all()

    print("User Proverbs:", [p.text for p in user_proverbs])
    print("User Tongue Twisters:", [t.text for t in user_twisters])
