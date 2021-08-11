from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine
from datetime import datetime

import discord

import time

import json
import os

cwd = os.getcwd()

Base = declarative_base()
engine = None
session = None


class GuildGame(Base):
    __tablename__ = 'guild_game'
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_created_at = Column(String(255))
    guild = Column(String(255))
    active = Column(Integer)
    live_initiative = Column(Integer)
    initiative_title = Column(String(255), default="")
    initiative_message = Column(Integer)


class Character(Base):
    __tablename__ = 'character'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(String(255))
    is_active = Column(Integer, default=1)
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
    start_of_day_stability = Column(Integer, default=80)
    unstable = Column(Integer, default=0)
    insane = Column(Integer, default=0)
    free_improvements = Column(Integer, default=0)
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
    passed_prev = Column(Integer)


class CharacterImprovementRequest(Base):
    __tablename__ = 'improvement_requests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer)
    improvement_message = Column(Integer)


class CharacterInitiative(Base):
    __tablename__ = 'character_initiative'
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild = Column(String(255))
    character_id = Column(Integer)
    init_result = Column(String(255))
    roll_result = Column(Integer)


engine = create_engine('sqlite:///config/steve_bot_storage.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
session = scoped_session(sessionmaker(bind=engine))
Base.metadata.create_all(engine)


########################################
####   GAME ACTIVITY                ####
########################################
def create_game_if_not_in_guild(guild):
    guild_id = str(guild.id)

    if get_game_for_guild(guild_id) is None:
        game = GuildGame(
            game_created_at=str(int(time.time() * 1000)),
            guild=guild_id,
            active=0
        )

        session = scoped_session(sessionmaker(bind=engine))
        session.merge(game)
        session.commit()


def get_game_for_guild(guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    return res


def set_game_active_for_guild(guild, active):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    res.active = active
    session.commit()


def is_game_active_for_guild(guild):
    return get_game_for_guild(guild).active == 1


###########################################
######          IMPROVEMENTS        #######
###########################################

def set_improvement_requested(character_id, message_id):
    session = scoped_session(sessionmaker(bind=engine))
    session.merge(CharacterImprovementRequest(
        character_id=character_id,
        improvement_message=message_id
    ))
    session.commit()


def get_improvement_request_from_message(message_id):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(CharacterImprovementRequest).filter_by(improvement_message=message_id).first()
    return res


def character_has_improvement_request(character_id):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(CharacterImprovementRequest).filter_by(character_id=character_id).all()
    return len(res) > 0


def remove_character_improvement_requests(character_id):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(CharacterImprovementRequest).filter_by(character_id=character_id).delete()
    session.commit()


###########################################
###         INITIATIVE CONTROLS        ####
###########################################
def start_initiative_in_guild(guild, message_id, title):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    res.live_initiative = 1
    res.initiative_message = message_id
    res.initiative_title = title
    session.commit()


def end_initiative_in_guild(guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    res.live_initiative = 0
    res.initiative_message = 0
    res.initiative_title = ""

    session.query(CharacterInitiative).filter_by(guild=guild).delete()

    session.commit()


def is_initiative_active_in_guild(guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    return res.live_initiative == 1


def get_initiative_results_for_guild(guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(CharacterInitiative).filter_by(guild=guild).all()
    return res


def get_initiative_message_id_for_guild(guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    return res.initiative_message


def get_initiative_title_for_guild(guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(GuildGame).filter_by(guild=guild).first()
    return res.initiative_title


def character_has_initiative_in_guild(character_id, guild):
    session = scoped_session(sessionmaker(bind=engine))
    res = session.query(CharacterInitiative).filter_by(guild=guild, character_id=character_id).first()
    return res is not None


def add_character_initiative_to_guild(guild, character_id, initiative_result, roll_result):
    session = scoped_session(sessionmaker(bind=engine))
    session.merge(CharacterInitiative(
        guild=guild,
        character_id=character_id,
        init_result=initiative_result,
        roll_result=roll_result
    ))
    session.commit()


def close_initiative_if_complete_in_guild(guild):
    if is_initiative_complete_for_guild(guild):
        end_initiative_in_guild(guild)


def is_initiative_complete_for_guild(guild):
    all_in_guild = get_characters_in_guild(guild, True, False)
    results_in_guild = get_initiative_results_for_guild(guild)

    return len(all_in_guild) == len(results_in_guild)


###########################################
####           CHARACTER CONTROLS      ####
###########################################
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
        create_default_skills_for_char(me_in_db)


def create_default_skills_for_char(character):
    with open(cwd + '/default_skills.json', 'r') as myfile:
        loaded_json = json.loads(myfile.read().replace('\n', ''))

        session = scoped_session(sessionmaker(bind=engine))

        for skill in loaded_json:
            session.merge(CharacterSkill(
                character_id=character.id,
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


def set_character_stability(character, value):
    char_id = character.id
    guild = character.guild_id

    session = scoped_session(sessionmaker(bind=engine))
    result = session.query(Character).filter_by(id=char_id, guild_id=guild).first()

    result.stability_curr = min(max(value, 0), character.stability_max)
    session.commit()


def mark_skill_as_passed(character_id, skill):
    session = scoped_session(sessionmaker(bind=engine))
    db_skill = session.query(CharacterSkill).filter_by(character_id=character_id, skill_name=skill).first()
    db_skill.passed_prev = 1
    session.commit()


def mark_skill_as_not_passed(character_id, skill):
    session = scoped_session(sessionmaker(bind=engine))
    db_skill = session.query(CharacterSkill).filter_by(character_id=character_id, skill_name=skill).first()
    db_skill.passed_prev = 0
    session.commit()


async def add_xp(character, xp, channel):
    char_id = character.id
    guild = character.guild_id

    session = scoped_session(sessionmaker(bind=engine))
    result = session.query(Character).filter_by(id=char_id, guild_id=guild).first()

    pre_xp = result.xp
    pre_level = result.level

    new_xp = result.xp + xp
    result.xp = new_xp

    xp_tracking = new_xp

    from commands.xp.xp import xp_to_level
    while True:
        try:
            if xp_tracking < 0:
                break

            if result.level < xp_to_level[xp_tracking]:
                ##LEVEL UP
                while result.level < xp_to_level[xp_tracking]:
                    result.level = result.level + 1
                    result.free_improvements = result.free_improvements + 2

                level_up_embed = discord.Embed(title=result.character_name + " is now Level " + str(result.level),
                                               description="You can now upgrade 2 skills for free! Do `?improve <skillname>` to improve it.",
                                               color=0x00ff00)
                await channel.send(embed=level_up_embed)

            break
        except KeyError:
            pass

        xp_tracking = xp_tracking - 1

    session.commit()
    return pre_xp, new_xp


def reset_day_stability(character):
    char_id = character.id
    guild = character.guild_id

    session = scoped_session(sessionmaker(bind=engine))
    result = session.query(Character).filter_by(id=char_id, guild_id=guild).first()

    result.start_of_day_stability = result.stability_curr

    session.commit()


def set_unstable(character, unstable=True):
    char_id = character.id
    guild = character.guild_id

    session = scoped_session(sessionmaker(bind=engine))
    result = session.query(Character).filter_by(id=char_id, guild_id=guild).first()

    if unstable:
        result.unstable = 1
        result.insane = 0
    else:
        result.unstable = 0

    session.commit()


def set_insanity(character, insane=True):
    char_id = character.id
    guild = character.guild_id

    session = scoped_session(sessionmaker(bind=engine))
    result = session.query(Character).filter_by(id=char_id, guild_id=guild).first()

    if insane:
        result.insane = 1
        result.unstable = 0
    else:
        result.insane = 0

    session.commit()


def has_improvement(character):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(id=character.id).first()
    return result.free_improvements > 0


def spend_improvement(character):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(id=character.id).first()
    result.free_improvements = result.free_improvements - 1

    session.commit()


def create_custom_skill(character_id, skill, value, modifier="NON"):
    session = scoped_session(sessionmaker(bind=engine))
    session.merge(CharacterSkill(character_id=character_id, skill_name=skill, pass_level=value, modifier=modifier))
    session.commit()


def set_skill(character_id, skill, value, reset_pass=False):
    session = scoped_session(sessionmaker(bind=engine))
    db_skill = session.query(CharacterSkill).filter_by(character_id=character_id, skill_name=skill).first()
    db_skill.pass_level = value

    if reset_pass:
        db_skill.passed_prev = 0

    session.commit()


def get_skill(character_id, skill_name):
    session = scoped_session(sessionmaker(bind=engine))
    db_skill = session.query(CharacterSkill).filter_by(character_id=character_id, skill_name=skill_name).first()
    if db_skill == None:
        return None

    return db_skill.pass_level


'''
owner - The discord user id that you want to fetch the user for, as a String
guild - The id of the guild running on
'''


def get_character_for_owner(owner, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(owner_id=owner, guild_id=guild, is_active=1).first()
    return result


def get_character_for_slug(slug, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(character_slug=slug, guild_id=guild).first()
    return result


def get_character_for_id(id):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(id=id, is_active=1).first()
    return result


def get_character_created_at(created_at, guild):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(created_at=created_at, guild_id=guild, is_active=1).first()
    return result


def get_characters_in_guild(guild, incl_npc=False, incl_inactive=True):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(guild_id=guild).all()

    if not incl_npc:
        result = [x for x in result if x.owner_id != "NPC"]

    if not incl_inactive:
        result = [x for x in result if x.is_active == 1]

    return result


def get_skills_for_character(character_id):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(CharacterSkill).filter_by(character_id=character_id).all()
    return result


def is_character_active(character_id):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(id=character_id).first()
    return result.is_active == 1


def set_character_activation(character_id, activation):
    session = scoped_session(sessionmaker(bind=engine))

    result = session.query(Character).filter_by(id=character_id).first()
    result.is_active = activation
    session.commit()
