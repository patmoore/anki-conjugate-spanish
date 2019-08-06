
"""

"""
from sqlalchemy import Column, Boolean, Integer, String

from conjugate_spanish.database.basedbo import BASE


class VerbConjugationOverride(BASE):
    """
    Holds the information about conjugation overrides that apply to a verb.
    """
    # This override is explicitly *excluded*
    negative = Column(Boolean)
    verb_id = Column(Integer)
    implied_by_id = Column(Integer)


class ConjugationOverride(BASE):
    """
    Database entry for the conjugation overrides.
    Is this really necessary?
    """
    short_code = Column(String(8))

