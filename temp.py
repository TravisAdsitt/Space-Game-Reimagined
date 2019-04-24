# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///space_game.db')




class Dimension(Base):
    __tablename__ = 'dimensions'
    
    id = Column(Integer, primary_key = True)
    time_started = Column(DateTime)

class Planet(Base):
    __tablename__ = 'planets'
    
    id = Column(Integer, primary_key=True)
    time_ratio = Column(Integer) #This is number of days in game to one IRL
    resource_count = Column(Integer)
    dimension_id = Column(Integer, ForeignKey('dimensions.id'))


"""
Helper function for get rewards
"""
def check_for_completed_tasks(player_id):
    return False

"""
This is to find out if there are any new completed tasks, and if there are
then we need to get the reward strings from them... these, now that I am 
thinking ahout it, should also include the taking away of things such as
focus if the person has been researching for a certain amount of time...
"""
def get_rewards(player_id):
    return False

def get_schedule(player_id):
    sched_q = session.query(Schedule).filter(Schedule.player_id==player_id).one()
    
    return sched_q

def get_dimension_start(player_id):
    player_q = session.query(Player).filter(Player.id == player_id).one()
    planet_q = session.query(Planet).filter(Planet.id == player_q.planet_id).one()
    start_time = session.query(Dimension).filter(Dimension.id == planet_q.dimension_id).one()
    start_time = start_time.time_started
    
    return start_time

def get_hour_of_day(player_id):
    start_time = get_dimension_start(player_id)
    now_time = datetime.datetime.now()
    total_seconds = (now_time - start_time).total_seconds()
    
    seconds_this_day = total_seconds % 86400
    minutes_this_day = seconds_this_day / 60
    hours_this_day = minutes_this_day / 60
    
    return hours_this_day
  
def get_number_of_days_IRL(player_id, start_time):
    if(start_time == None):
        start_time = get_dimension_start(player_id)
    now_time = datetime.datetime.now()
    total_seconds = (now_time - start_time).total_seconds()
    
    days = total_seconds / 86400
    
    return days

def get_number_of_days_IG(player_id, start_time):
    IRL_days = get_number_of_days_IRL(player_id,start_time)
    player_q = session.query(Player).filter(Player.id == player_id).one()
    planet_q = session.query(Planet).filter(Planet.id == player_q.planet_id).one()
    time_ratio = planet_q.time_ratio
    
    days = IRL_days * time_ratio
    return days


def get_schedule_stats_deltas(player_id):
    sched = get_schedule(player_id)
    vectors = {}
    
    energy_d = 0
    focus_d = 0
    perspective_d = 0
    
    sleep_time = sched.time_sleeping
    gather_time = sched.time_gathering
    build_time = sched.time_building
    research_time = sched.time_researching
    
    #Sleeping
    focus_d = sleep_time * 12.5
    energy_d = sleep_time * 12.5
    
    #Gathering
    perspective_d = gather_time
    energy_d = energy_d - (10 * gather_time)
    
    #Building
    energy_d = energy_d - (5 * build_time)
    
    #Researching
    energy_d = energy_d - (5 * research_time)
    perspective_d = perspective_d + (5 * research_time)
    focus_d = focus_d - (10 * research_time)
    
    vectors["energy"] = energy_d
    vectors["focus"] = focus_d
    vectors["perspective"] = perspective_d
    
    return vectors
    
    
    

def set_current_stats(player_id):
    player_q = session.query(Player).filter(Player.id == player_id).one()
    sched = get_schedule(player_id)
    start_time = get_dimension_start(player_id)
    
    
    if(player_q.last_updated != None):
        start_time = player_q.last_updated
     
    num_days = get_number_of_days_IG(player_id,start_time)
    stat_deltas = get_schedule_stats_deltas(player_id)
    
    energy_c = player_q.energy_count
    focus_c = player_q.focus_count
    perspective_c = player_q.perspective_count
    
    energy_d = stat_deltas["energy"]
    focus_d = stat_deltas["focus"]
    perspective_d = stat_deltas["perspective"]
#    print("energy_d: %d -- focus_d: %d -- perspective_d: %d" % \
#          (energy_d,focus_d,perspective_d))
#    s_time = sched.time_sleeping
#    g_time = sched.time_gathering
#    b_time = sched.time_building
    r_time = sched.time_researching
    
    for x in range(int(num_days)):
        temp_e = energy_c + energy_d
        temp_f = focus_c + focus_d
        temp_p = perspective_c + perspective_d
        
        #adjusting deltas looking for reasons not to give rewards
        if(temp_e < 0):
            energy_d = -energy_c
            perspective_d = 0
        if(temp_f < 0):
            focus_d = -focus_c
            if(temp_e > -1 and perspective_d > 0):
                perspective_d = perspective_d - (5 * r_time)
        
        temp_e = energy_c + energy_d
        temp_f = focus_c + focus_d
        temp_p = perspective_c + perspective_d
        
        energy_c = temp_e
        focus_c = temp_f
        perspective_c = temp_p
        
    #Might need to look into how to update for mid-day stats...
    player_q.energy_count = energy_c
    player_q.focus_count = focus_c
    player_q.perspective_count = perspective_c
            
    
    

def get_current_activity(player_id):
    current_hour = get_hour_of_day(player_id)
    sched = get_schedule(player_id) 
    
    #Sleep -> Gather -> Build -> Research
    current_hour = current_hour - sched.time_sleeping
    if(current_hour < 1):
        return "Sleeping"
    current_hour = current_hour - sched.time_gathering
    if(current_hour < 1):
        return "Gathering"
    current_hour = current_hour - sched.time_building
    if(current_hour < 1):
        return "Building"
    current_hour = current_hour - sched.time_researching
    if(current_hour < 1):
        return "Researching"
    
    return "UNKNOWN"
    
def set_current_activity(player_id):
    player_q = session.query(Player).filter(Player.id == player_id).one()
    player_q.current_activity = get_current_activity(player_id)
    
class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    username = Column(String)
    energy_count = Column(Integer)
    focus_count = Column(Integer)
    perspective_count = Column(Integer)
    current_activity = Column(String)
    last_updated = Column(DateTime)
    planet_id = Column(Integer, ForeignKey('planets.id'))
    
    def __repr__(self):
        return \
    "<Player(username='%s', energy_count='%d', focus_count='%d', perspective_count='%d', current_activity='%s')>" % \
        (self.username,self.energy_count,self.focus_count,self.perspective_count,self.current_activity)
    
    def update(self):
        set_current_stats(self.id)
        set_current_activity(self.id)
        self.last_updated = datetime.datetime.now()
        session.commit()
        
    def get_status(self):
        ret_string = "Energy: %d -- Focus: %d -- Perspective: %d -- Currently: %s\n" % \
    (self.energy_count,self.focus_count,self.perspective_count,self.current_activity)
        sched = get_schedule(self.id)
        ret_string = ret_string + \
        ("Sleeping %d hrs --> Gathering %d hrs --> Building %d hrs --> Researching: %d hrs" % \
         (sched.time_sleeping,sched.time_gathering,sched.time_building,sched.time_researching))
        
        return ret_string
    
    def add_energy(self, amount):
        self.energy_count = self.energy_count + amount
        
    def add_focus(self, amount):
        self.focus_count = self.focus_count + amount
    
    def add_perspective(self, amount):
        self.perspective_count = self.perspective_count + amount
                

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True)
    time_gathering = Column(Integer)
    time_building = Column(Integer)
    time_researching = Column(Integer)
    time_sleeping = Column(Integer)
    player_id = Column(Integer, ForeignKey('players.id'))
    
    def __repr__(self):
        return \
    "<Schedule(time_gathering='%d', time_building='%d', time_researching='%d', time_sleeping='%d')>" % \
    (self.time_gathering,self.time_building,self.time_researching,self.time_sleeping)
    
    def update(self, session):
        session.commit()
    

def update_building_table():
    return False

class Build_Item(Base):
    __tablename__ = "build"
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    reward_cmd = Column(String)
    task_name = Column(String)
    reward_recieved = Column(Boolean)
    player_id = Column(Integer, ForeignKey('players.id'))
    
    def __repr__(self):
        return \
    "<Build_Item(start_time='%s', end_time='%s', reward_cmd='%s', task_name='%s', reward_recieved='%s', player_id='%d')>" % \
    (self.start_time,self.end_time,self.reward_cmd,self.task_name,self.reward_recieved,self.player_id)
        
    


def check_user_exists(username):
    user_q = session.query(Player.username).\
    filter(Player.username == username)
    
    if(user_q.count() > 0):
        return True
    else:
        return False

def new_player_signup():
    
    new_username = ""
    
    while (new_username == ""):
        temp_username = input("Please input a username:")
        
        if(check_user_exists(temp_username)):
            print("Sorry that is already taken, please enter a different one...")
        else:
            new_username = temp_username
    
    plan = session.query(Planet).first()
    
    new_player = Player(username=new_username,energy_count=100,focus_count=25,perspective_count=5,current_activity="Starting",planet_id=plan.id)
    session.add(new_player)
    session.commit()
    
    print("There are 24 hours in a day...")
    while True:
        time_remaining = 24
        sleep_time = int(input("How many would you like to spend sleeping(%d)?" % time_remaining))
        time_remaining = time_remaining - sleep_time
        gather_time = int(input("How many would you like to spend gathering(%d)?" % time_remaining))
        time_remaining = time_remaining - gather_time
        build_time = int(input("How many would you like to spend building(%d)?" % time_remaining))
        time_remaining = time_remaining - build_time
        research_time = int(input("How many would you like to spend researching(%d)?" % time_remaining))
        time_remaining = time_remaining - research_time
        if(time_remaining == 0):
            break
        else:
            print("I am sorry those didn't add up to 24, try again...")
    
    new_schedule = Schedule(time_sleeping=sleep_time,
                            time_gathering=gather_time,
                            time_building=build_time,
                            time_researching=research_time,
                            player_id=new_player.id)
    session.add(new_schedule)
    session.commit()
    
    print("User created! Please login!")    


def user_login():
    current_user = ""
    
    while (current_user == ""):
        user_input = input("Please enter your username(If you need an account just hit enter, or q to quit):")
        
        new_player = (user_input == "")
        
        if(user_input.lower() == "q"):
            return "q"
    
        if(new_player):
            new_player_signup()
        else:
            if(check_user_exists(user_input)):
                current_user = user_input
            else:
                print("Username does not exist... Please try again or sign-up")
                
    return current_user

def big_bang():
    dimen_q = session.query(Dimension)
    if(dimen_q.count() < 1):
        new_dimension = Dimension(time_started=datetime.datetime.now())
        session.add(new_dimension)
        session.commit()
    dimen = dimen_q.first()
    plan_q = session.query(Planet)
    if(plan_q.count() < 1):
        new_planet = Planet(resource_count = 700, time_ratio = 7, dimension_id = dimen.id)
        session.add(new_planet)
        session.commit()
    
    
def menu():
    print("Research Queue: 'rq' -- Build Queue: 'bq' -- Schedule: 's' -- Refresh: 'r'")

def game():
    
    big_bang()
    
    current_username = user_login()
    
    if(current_username == "q"):
        return False
    
    current_user = session.query(Player).filter(Player.username == current_username).one()
    current_user.update()
    print("Welcome %s!" % current_user.username)
    print(current_user.get_status())
    

"""
MAIN GAME HERE
"""

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


game()
    
    
    





































