from conjugate_spanish.database.basedbo import BASE
from sqlalchemy import Column, Integer, String, Boolean


class Verb(BASE):
    __tablename__ = 'users'

    base_verb_id = Column(Integer)

    prefix_words = Column(String(50))
    prefix = Column(String(10))
    core_characters = Column(String(25))
    inf_ending = Column(Integer)
    reflexive = Column(Boolean)
    suffix_words = Column(String(50))
    explicit_no_root_verb = Column(Boolean)
