from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine
from datetime import datetime

import json
import os
cwd = os.getcwd()

Base = declarative_base()
engine = None
session = None


class Character(Base):
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255))
    character_image = Column(String(255), default="")
    character_name = Column(String(255), default="Character")
    character_slug = Column(String(255), default="char")
    owner_id = Column(String(255), default="NPC")
    guild_id = Column(String(255))
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    strength = Column(Integer, default=50)
    education = Column(Integer, default=50)
    power = Column(Integer, default=50)
    size = Column(Integer, default=50)
    dexterity = Column(Integer, default=50)
    constitution = Column(Integer, default=50)
    appearance = Column(Integer, default=50)
    intelligence = Column(Integer, default=50)
    hitpoints_max = Column(Integer, default=20)
    hitpoints_curr = Column(Integer, default=20)
    stability_max = Column(Integer, default=80)
    stability_curr = Column(Integer, default=80)
    speed = Column(Integer, default=60)

    def get_modifier(self, value):
        modifiers = {
            80: -5,
            70: -4,
            60: -3,
            50: -2,
            40: -1
        }

        while value not in modifiers.keys():
            value -= 1

            if value == 0:
                return 0

        chosen = modifiers[value]
        return chosen

    def get_stat(self, stat):
        return getattr(self, stat)

    def set_stat(self, stat, value):
        setattr(self, stat, value)

class CharacterSkill(Base):
    __tablename__ = 'skill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer)
    synonyms = Column(String(255))
    skill_name = Column(String(255))
    pass_level = Column(Integer)
    modifier = Column(String(255))


engine = create_engine('sqlite:///steve_bot_storage.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))
Base.metadata.create_all(engine)


def user_has_character_in_guild(owner, guild):
    char = get_character_for_owner(owner, guild)
    return char is not None


def add_update_character_to_db(character):
    session = scoped_session(sessionmaker(bind=engine))
    session.merge(character)
    session.commit()


def add_character_to_db(character, add_skills=False):
    add_update_character_to_db(character)

    me_in_db = get_character_created_at(character.created_at, character.guild_id)

    if add_skills:
        with open(cwd + '/default_skills.json', 'r') as myfile:
            loaded_json = json.loads(myfile.read().replace('\n', ''))

            session = scoped_session(sessionmaker(bind=engine))

            for skill in loaded_json:
                session.merge(CharacterSkill(
                    character_id=me_in_db.id,
                    skill_name=skill['name'],
                    synonyms=",".join(skill['synonyms']),
                    pass_level=int(skill['default_value']),
                    modifier=skill['modifier']))

            session.commit()


def set_character_stat(character, stat, value):
    char_id = character.id
    guild = character.guild_id

    session = scoped_session(sessionmaker(bind=engine))
    result = session.query(Character).filter_by(id=char_id, guild_id=guild).first()

    result.set_stat(stat, value)
    session.commit()


def create_custom_skill(character_id, skill, value, modifier="NON"):
    session = scoped_session(sessionmaker(bind=engine))
    session.merge(CharacterSkill(character_id=character_id, skill_name=skill, pass_level=value, modifier=modifier))
    session.commit()


def set_skill(character_id, skill, value):
    session = scoped_session(sessionmaker(bind=engine))
    db_skill = session.query(CharacterSkill).filter_by(character_id=character_id, skill_name=skill).first()
    db_skill.pass_level = value
    session.commit()


def get_skill(character_id, skill):
    session = scoped_session(sessionmaker(bind=engine))
    db_skill = session.query(CharacterSkill).filter_by(character_id=character_id, skill_name=skill).first()
    return db_skill.pass_level


'''
owner - The discord user id that you want to fetch the user for, as a String
guild - The id of the guild running on
'''
def get_character_for_owner(owner, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(owner_id=owner, guild_id=guild).first()
    return result


def get_character_for_name(name, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(character_name=name, guild_id=guild).first()
    return result


def get_character_for_slug(slug, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(character_slug=slug, guild_id=guild).first()
    return result


def get_character_for_id(id, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(id=id, guild_id=guild).first()
    return result


def get_character_created_at(created_at, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(created_at=created_at, guild_id=guild).first()
    return result


def get_characters_in_guild(guild, incl_npc = False):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(guild_id=guild).all()

    if incl_npc:
        return result
    else:
        result = [x for x in result if x.owner_id != "NPC"]
        # result = list(filter((x for x in result if x.owner_id != "NPC"), result))
        return result


def get_skills_for_character(character_id):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(CharacterSkill).filter_by(character_id=character_id).all()
    return result