from sqlalchemy import Column, String, Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    player_id = Column(String, primary_key=True)   # Cricsheet registry hash
    name = Column(String, nullable=False)
    bowling_style = Column(String, nullable=True)   # filled in later via Cricinfo
    batting_style = Column(String, nullable=True)
    dob = Column(Date, nullable=True)


class Match(Base):
    __tablename__ = "matches"

    match_id = Column(String, primary_key=True)     # Cricsheet filename
    date = Column(Date, nullable=False)
    venue = Column(String)
    city = Column(String)
    team1 = Column(String)
    team2 = Column(String)
    toss_winner = Column(String)
    toss_decision = Column(String)
    match_winner = Column(String, nullable=True)
    match_type = Column(String)   # T20 / ODI / Test
    player_of_match = Column(String, nullable=True)


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"))
    innings_team = Column(String)
    over_num = Column(Integer)
    ball_num = Column(Integer)
    batsman = Column(String)
    bowler = Column(String)
    non_striker = Column(String)
    runs_batsman = Column(Integer)
    runs_extras = Column(Integer)
    runs_total = Column(Integer)
    is_wicket = Column(Boolean, default=False)
    wicket_kind = Column(String, nullable=True)
    player_out = Column(String, nullable=True)