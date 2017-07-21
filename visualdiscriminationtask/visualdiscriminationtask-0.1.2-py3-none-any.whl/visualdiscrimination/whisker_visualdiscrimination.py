#!/usr/bin/env python
# whisker_visualdiscrimination.py

# Assumes

# =============================================================================
# Imports, and configure logging
# =============================================================================

import logging
import random
from attrdict import AttrDict
from datetime import datetime
from twisted.internet import reactor
from whisker.logging import configure_logger_for_colour
from whisker.constants import DEFAULT_PORT
from whisker.convenience import (load_config_or_die,
                                 connect_to_db_using_attrdict,
                                 insert_and_set_id,
                                 ask_user,
                                 save_data)
from whisker.twistedclient import WhiskerTask
from whisker.api import (Rectangle,Brush,Pen,DocEventType,PointType,VerticalAlign,HorizontalAlign,BLACK)
import yaml

log = logging.getLogger(__name__)
configure_logger_for_colour(log)

log.setLevel(logging.DEBUG)  # debug-level logging for this file...
logging.getLogger("whisker").setLevel(logging.DEBUG)  # ... and for Whisker

# =============================================================================
# Constants
# =============================================================================

TASKNAME_SHORT = "visualdiscrimination"  # no spaces; we'll use it in a filename
TASKNAME_LONG = "Visual Discrimination Task"

# Our tables. They will be autocreated. (NOTE: do not store separate copies of
# table objects, as they can get out of sync as new columns area created.)
SESSION_TABLE = 'session'
TRIAL_TABLE = 'trial'
SUMMARY_TABLE = 'summary'

# All the supported conditional changes. Conditions in the config must have a 
# type that matches a key value here (e.g. "consecutive rewarded responses")
CONDITIONAL_CHANGE_TYPES=[
    AttrDict({'key':"trials"}),
    AttrDict({'key':"total responses",'get_num_responses_params':{'total':True}}),
    AttrDict({'key':"consecutive rewarded responses",'get_num_responses_params':{
        'consecutive':True,'rewarded':True}
    }),
    AttrDict({'key':"consecutive unrewarded responses",'get_num_responses_params':{
        'consecutive':True,'rewarded':False}
    }),
    AttrDict({'key':"total rewarded responses",'get_num_responses_params':{
        'consecutive':False,'rewarded':True}
    }),
    AttrDict({'key':"total unrewarded responses",'get_num_responses_params':{
        'consecutive':False,'rewarded':False}
    }),
]

# Generate names for the UI elements associated with each change type
for cc in CONDITIONAL_CHANGE_TYPES:
    cc['whisker_obj_name']=cc.key.replace(" ","_")

def print_conditional_change_effect(change,future_tense):
    if future_tense:
        log.info("  {0} will be altered".format(change.key))
        if "enabled" in change:
            log.info("    It will be {0}".format("Enabled" if change.enabled else "Disabled"))
    else:
        log.info("  {0} has been altered".format(change.key))
        if "enabled" in change:
            log.info("    It has been {0}".format("Enabled" if change.enabled else "Disabled"))
    if "stimuli" in change:
        for s in change.stimuli:
            log.info("    {0} will now reward {1:.2%} of the time".format(s.key,s.reward_ratio))

def print_conditional_change(spec,future_tense=False):
    if future_tense:
        log.info("After {0!s} {1} the following changes will occur".format(spec.trials if "trials" in spec else spec.responses,spec.type))
    else:
        log.info("Condition Triggered: {0!s} {1} met".format(spec.trials if "trials" in spec else spec.responses,spec.type))
    for chng in spec.changes:
        print_conditional_change_effect(chng,future_tense)


# =============================================================================
# The task itself
# =============================================================================

class VisualDiscriminationTask(WhiskerTask):
    def __init__(self, config, db, session):
        """Here, we initialize the task, and store any relevant variables."""
        super().__init__()  # call base class init
        self.config = config
        self.db = db
        self.session = session
        self.trial_num = 0
        self.reward_sequence=[] # A sequence of booleans indicating whether 
                                # rewards occured. Cannot be indexed as it does
                                # not take skipped trials into account
    
    def fully_connected(self):
        """At this point, we are fully connected to the Whisker server."""
        log.info("Task running.")
        random.seed()

        whisker=self.whisker
        config=self.config
        
        whisker.timestamps(True)
        whisker.report_name(TASKNAME_LONG)
        whisker.get_network_latency_ms()
        whisker.claim_display(group="box0",device="CAGEDISPLAY", alias="screen")
        whisker.display_get_size("screen")
        
        whisker.display_create_document("start")
        screen_width=config.screen_resolution.width
        screen_centre_x=int(screen_width/2)
        screen_height=config.screen_resolution.height
        screen_centre_y=int(screen_height/2)
        self.screen_centre_x=screen_centre_x
        whisker.display_set_document_size("start",screen_width,screen_height)
        rect=Rectangle(screen_centre_x-100,screen_height-80,width=200,height=60)
        pen=Pen()
        brush=Brush()
        whisker.display_add_obj_rectangle("start","startbutton",rect,pen,brush)
        whisker.display_scale_documents("screen",True)
        whisker.display_set_event("start","startbutton","started",DocEventType.touch_down)
        whisker.display_set_event("start","startbutton","started",DocEventType.mouse_down)

        whisker.display_create_document("summary")
        whisker.display_set_background_colour("summary",[80,80,80])
        self.state_screen_width=config.overview_screen_resolution.width
        self.state_screen_height=config.overview_screen_resolution.height
        self.state_screen_centre_x=int(self.state_screen_width/2)
        self.state_screen_centre_y=int(self.state_screen_height/2)
        
        whisker.display_set_document_size("summary",self.state_screen_width,self.state_screen_height)
        whisker.display_add_obj_text("summary","state",[40,40],"State: None",50)
        y=90
        for cond in CONDITIONAL_CHANGE_TYPES:
            whisker.display_add_obj_text("summary",cond.whisker_obj_name,[40,y], cond.key + ": 0",50)
            y+=60
        whisker.display_scale_documents("summary",True)
        
        if whisker.claim_display(group="human",device="HUMANDISPLAY", alias="overview"):
            whisker.display_show_document("overview","summary")

        stimuli={}
        for s in config.stimuli:
            stimuli[s.key]=s.file

        self.stimuli_screens={}
        self.trial_order=[None]*config.num_trials
        fixed_trials=0
        for p in config.pairings:
            whisker.display_create_document(p.key)
            whisker.display_set_document_size(p.key,screen_width,screen_height)
            left=p.stimuli[0].key
            whisker.display_add_obj_bitmap(p.key,left,[screen_centre_x-200,screen_centre_y],stimuli[left],False,-1,-1,VerticalAlign.middle,HorizontalAlign.centre)
            right=p.stimuli[1].key
           
            whisker.display_add_obj_bitmap(p.key,right,[screen_centre_x+200,screen_centre_y],stimuli[right],False,-1,-1,VerticalAlign.middle,HorizontalAlign.centre)
            whisker.display_set_event(p.key,left,left,DocEventType.touch_down)
            whisker.display_set_event(p.key,left,left,DocEventType.mouse_down)
            whisker.display_set_event(p.key,right,right,DocEventType.touch_down)
            whisker.display_set_event(p.key,right,right,DocEventType.mouse_down)
            p.stimuli_by_key={}
            p.stimuli_by_key[p.stimuli[0].key]=p.stimuli[0]
            p.stimuli_by_key[p.stimuli[1].key]=p.stimuli[1]
            
            p["occurances"]=0
            p["last_trial_occarance"]=-1
            self.stimuli_screens[p.key]=p

            if "fixed_rate" in p.frequency:
                for i in range(p.frequency.fixed_rate_start,config.num_trials,p.frequency.fixed_rate):
                    self.trial_order[i]=p
                    fixed_trials+=1

        unused_screens=config.num_trials-fixed_trials
        unassigned_screens=[]
        for k,s in self.stimuli_screens.items():
            if "appearance_ratio" in s.frequency:
                s.total_occurances=int(s.frequency.appearance_ratio*unused_screens+0.5)
                unassigned_screens+=[s]*s.total_occurances

        random.shuffle(unassigned_screens)
        for i in range(config.num_trials):
            if self.trial_order[i] is None:
                self.trial_order[i]=unassigned_screens.pop()

        log.info("--------")
        index_gen=range(len(self.trial_order))
        log.info("Trials in Order:")
        log.info(("\n").join(["{0!s}: {1.key}".format(i,t) for (i,t) in zip(index_gen,self.trial_order)]))
        log.info("--------")


        if "conditions" in config:
            self.conditional_changes=config.conditions
            log.info("These changes may occur")
            for c in self.conditional_changes:
                log.info("After {0!s} {1} the following changes will occur".format(c.trials if "trials" in c else c.responses,c.type))
                for chng in c.changes:
                    print_conditional_change_effect(chng)
        log.info("--------")

        whisker.claim_audio(0,alias="speakers")
        whisker.timer_set_event("stimuli_selection",config.iti_millis)
        whisker.timer_set_event("task_time_out",config.max_task_time_millis)
        whisker.claim_line(device="HOUSELIGHT",group="box0",output=True,alias="house_lights")
        whisker.claim_line(device="TRAYLIGHT",group="box0",output=True,alias="tray_lights")
        whisker.claim_line(device="PELLET",group="box0",output=True,alias="pellet_dispenser")
        whisker.claim_line(device="IRBEAM",group="box0",alias="ir_beam")
        whisker.line_set_state("ir_beam",True)

        self.set_state("iti")

    def set_state(self,state):
        self.state=state
        whisker=self.whisker
        whisker.display_delete_obj("summary","state")
        whisker.display_delete_obj("summary","selection")
        whisker.display_add_obj_text("summary","state",[20,20],"State: "+ state,50,None,False,False,0,[255,255,255])
        
        y=100
      
        if hasattr(self, "selection_screen"):
            y=60
            for s in self.selection_screen.stimuli:
                whisker.display_add_obj_text("summary","selection",[60,y],s.key,50,None,False,False,0,[255,255,255])
                y+=60
                whisker.display_add_obj_text("summary","selection",[100,y],str(s.reward_ratio*100)+"%",50,None,False,False,0,[255,255,255])
                y+=60
        y=40
        for cond in CONDITIONAL_CHANGE_TYPES:
            whisker.display_delete_obj("summary",cond.whisker_obj_name)
            if "get_num_responses_params" in cond:
                value=self.get_num_responses(**cond.get_num_responses_params)
                text=cond.key+": " + str(value)
                whisker.display_add_obj_text("summary",cond.whisker_obj_name,[self.screen_centre_x,y], text,50)
            else:
                text=cond.key+": " + str(self.trial_num)
                whisker.display_add_obj_text("summary",cond.whisker_obj_name,[self.screen_centre_x,y], text,50)
            y+=60

    def get_num_responses(self,total=False,consecutive=False,rewarded=False):
        num=0
        if consecutive:
            for i in reversed(self.reward_sequence):
                if rewarded==i:
                    num+=1
                else:
                    break
        else:
            num=len(list(i for i in self.reward_sequence if i==rewarded or total))
        return num

    def implement_change(self, change):
        print_conditional_change(change)
                    
        for screen_change in change.changes:
            screen=self.stimuli_screens[screen_change.key]
            if "enabled" in screen_change: 
                screen.enabled=screen_change.enabled
            if "stimuli" in screen_change:
                for stimuli_change in screen_change.stimuli:
                    stimuli=screen.stimuli_by_key
                    stimuli.reward_ratio=stimuli_change.reward_ratio

    def checkConditions(self):
        for c in self.conditional_changes:
            c.expired=False
            if c.type=="trials":
                if self.trial_num>=c.trials:
                    log.info("Change: ")
                    self.implement_change(c)
                    c.expired=True
            else:
                cond_type=next(ct for ct in CONDITIONAL_CHANGE_TYPES if ct.key==c.type)
                value=self.get_num_responses(**cond_type.get_num_responses_params)
                if value>c.responses:
                    self.implement_change(c)
                    c.expired=True
        self.conditional_changes=[c for c in self.conditional_changes if not c.expired]

    def incoming_event(self, event, timestamp=None):
        """An event has arrived from the Whisker server."""
        # timestamp is the Whisker server's clock time in ms; we want real time
        now = datetime.utcnow()
        whisker=self.whisker
        config=self.config
        print("Event: {e} (timestamp {t}, real time {n})".format(
            e=event, t=timestamp, n=now.isoformat()))
        whisker.audio_play_wav("speakers","13635__traveler__cork.wav")
        if event=="flash":
            if self.flashCount%2==1:
                pen=Pen(colour=BLACK)
                brush=Brush(colour=BLACK)
                whisker.display_add_obj_rectangle(self.selection_screen.key,"mask",self.flashmask,pen,brush)
            else:
                whisker.display_delete_obj(self.selection_screen.key,"mask")
            self.flashCount+=1
            return
        if self.state=="iti":
            self.set_state("start")
            whisker.display_show_document("screen","start")
            self.checkConditions()
        elif self.state=="start":
            self.selection_screen=self.trial_order[self.trial_num]
            while not self.selection_screen.enabled:
                trial = AttrDict(
                    session_id=self.session.id,  # important foreign key
                    trial_num=self.trial_num,
                    selected="SKIPPED",
                    when=now,
                    stimuli_left=self.selection_screen.stimuli[0].key,
                    stimuli_right=self.selection_screen.stimuli[1].key,
                    rewarded=False,
                )
                insert_and_set_id(self.db[TRIAL_TABLE], trial) 
                self.trial_num+=1
                self.selection_screen=self.trial_order[self.trial_num]
            whisker.display_show_document("screen",self.selection_screen.key)
            self.set_state("selection")
            whisker.timer_set_event("stimuli_selection_timeout",config.stimuli_presentation_millis,0)
        elif self.state=="selection":
            whisker.display_delete_obj("summary","choice")
            whisker.display_add_obj_text("summary","choice",[
                self.state_screen_centre_x,self.state_screen_centre_y+60]
                ,"Selected: "+event,50,None,False,False,0,[255,255,255])
                
            if event=="stimuli_selection_timeout":
                self.set_state("iti")
                whisker.display_blank("screen")
                self.correctResponse=False
            else:
                self.set_state("feedback")
                whisker.timer_set_event("feedback",config.feedback_millis,0)
                whisker.timer_set_event("flash",config.feedback_flash_millis,4*3-2)
                self.flashmask=whisker.display_get_object_extent(self.selection_screen.key,event)
                if self.flashmask:
                    pen=Pen(colour=BLACK)
                    brush=Brush(colour=BLACK)
                    whisker.display_add_obj_rectangle(self.selection_screen.key,"mask",self.flashmask,pen,brush)
                    self.flashCount=0

                rewards=False
                for s in self.selection_screen.stimuli:
                    if s.key==event:
                        rewards=s.reward_ratio>=random.random()
                        if "extinction_rate" in s:
                            s.reward_ratio-=s.extinction_rate
                self.correctResponse=rewards
            whisker.timer_clear_event("stimuli_selection_timeout")

            whisker.display_add_obj_text("summary","choice",[
                self.state_screen_centre_x,self.state_screen_centre_y+120]
                ,"Rewarded: "+str(self.correctResponse),50,None,False,False,0,[255,255,255])
            
            trial = AttrDict(
                session_id=self.session.id,  # important foreign key
                trial_num=self.trial_num,
                selected=event, # either time out or the symbol pressed
                when=now,
                stimuli_left=self.selection_screen.stimuli[0].key,
                stimuli_right=self.selection_screen.stimuli[1].key,
                rewarded=self.correctResponse,
            )
            insert_and_set_id(self.db[TRIAL_TABLE], trial)  # save to database
            self.reward_sequence.append(self.correctResponse)
            self.trial_num += 1
            log.info("{} event received so far".format(self.trial_num))

        elif self.state=="feedback":
            whisker.display_blank("screen")
           
            if self.correctResponse:
                self.set_state("collect_reward")
                whisker.line_set_state("tray_lights",True)
                whisker.line_set_event("ir_beam","beam_broken")
            else:
                whisker.line_set_state("house_lights",True)
                self.set_state("timeout")
                whisker.timer_set_event("timeout",config.timeout_millis,0)
                
        elif event=="timeout" or event=="beam_broken":
            if event=="timeout":
                whisker.line_set_state("house_lights",False)
            else:
                whisker.line_set_state("tray_lights",False)
                whisker.line_clear_event("beam_broken")
            self.set_state("iti")
            whisker.timer_set_event("stimuli_selection",config.iti_millis)
        
        if self.trial_num>=self.config.num_trials or event == "task_time_out":
            reactor.stop()  # stops Twisted and thus network processing
    

def assertIn(a,b,msg):
    if a not in b:
        log.error(msg)
        return False
    return True


def assertNone(a,msg):
    if a is not None:
        log.error(msg)
        return False
    return True

def assertNotIn(a,b,msg):
    if a in b:
        log.error(msg)
        return False
    return True

def assertEqual(a,b,msg):
    if a != b:
        log.error(msg)
        return False
    return True

def assertHasOne(a,propertyList,msg):
    matches=list(prop in a for prop in propertyList).count(True)==1
    if not matches:
        log.error(msg)
        return False
    return True

def assertMatchesOne(a,valueList,msg):
    matches=valueList.count(a)==1
    if not matches:
        log.error(msg)
        return False
    return True    

def validate(config):
    log.info("Validating config file")
    assertIn("stimuli_presentation_millis",config,"Config is missing stimuli_presentation_millis key")
    assertIn("iti_millis",config,"Config is missing iti_millis key")
    assertIn("feedback_millis",config,"Config is missing feedback_millis key")
    assertIn("feedback_flash_millis",config,"Config is missing feedback_flash_millis key")
    assertIn("timeout_millis",config,"Config is missing timeout_millis key")
    assertIn("num_trials",config,"Config is missing num_trials key")
    assertIn("max_task_time_millis",config,"Config is missing max_task_time_millis key")
    assertIn("stimuli",config,"Config is missing stimuli key")
    assertIn("screen_resolution",config,"Config is missing screen_resolution key")
    if "screen_resolution" in config: 
        assertIn("width",config.screen_resolution,"screen_resolution is missing width key")
        assertIn("height",config.screen_resolution,"screen_resolution is missing height key")
    stimuli={}
    for i in range(len(config.stimuli)):
        s=config.stimuli[i]
        warning_text="Config Error: stimuli " + str(i)
        assertIn("key",s,warning_text + " is missing key")
        assertIn("file",s,warning_text + " is missing file key")
        stimuli[s.key]=True
    
    assertIn("pairings",config,"Config is missing pairings key")
    fixed_occurances={}
    pairings_keys={}
    for i in range(len(config.pairings)):
        p=config.pairings[i]
        warning_text="Config Error: pairings " + str(i)
        assertIn("key",p,warning_text + " is missing key")
        pairings_keys[p.key]=True
        assertIn("stimuli",p,warning_text + " is missing stimuli key")
        assertEqual(len(p.stimuli),2,warning_text + " does not have 2 stimuli")
        for s in p.stimuli:
            assertIn("key",s,warning_text + " has stimuli with missing key")
            assertIn(s.key,stimuli,warning_text + ". Undefined stimuli key " + s.key)
            assertIn("reward_ratio",s,warning_text + ". Stimuli " + s.key + " has no reward_ratio key")
        assertIn("frequency",p,warning_text + " has no frequency key")
        if "fixed_rate" in p.frequency:
            assertIn("fixed_rate_start",p.frequency,warning_text + " specifes fixed rate, but is missing fixed_rate_start")
            for k in range(p.frequency.fixed_rate_start,config.num_trials,p.frequency.fixed_rate):
                assertNotIn(k,fixed_occurances,warning_text + " fixed rate occurances clash with a earlier sequence")
        else:
            assertIn("appearance_ratio",p.frequency,warning_text + " specifes is not fixed rate, but is missing appearance_ratio key")

    if "conditions" in config:
        valid_conditions=[cond.key for cond in CONDITIONAL_CHANGE_TYPES]
        for i in range(len(config.conditions)):
            c=config.conditions[i]
            warning_text="Config Error: condition " + str(i)
            assertIn("type",c,warning_text + " has no type key")
            assertIn("changes",c,warning_text + " has no changes key")
            assertMatchesOne(c.type,valid_conditions, warning_text + " type does not match valid conditional change types " + ",".join(valid_conditions))
            for chng in c.changes:
                assertIn("key",chng,warning_text + " change has no key")
                assertIn(chng.key,pairings_keys,warning_text + " change refers to unrecognised pairing key")
                if "stimuli" in chng:
                    for s in chng.stimuli:
                        assertIn(s.key,stimuli,warning_text + " " + str(s.key) + " does match specified keys")
                        assertIn("reward_ratio",s,warning_text + " stimuli change has no reward ratio key")

# =============================================================================
# Main execution sequence
# =============================================================================
def main():
    # -------------------------------------------------------------------------
    # Load config; establish database connection; ask the user for anything else
    # -------------------------------------------------------------------------
    
    log.info("Asking user for config filename")
    config = load_config_or_die(
        mandatory=['database_url','stimuli_presentation_millis','iti_millis','feedback_millis','feedback_flash_millis','timeout_millis','num_trials','max_task_time_millis','stimuli','screen_resolution','pairings'],
        defaults=dict(server='localhost', port=DEFAULT_PORT),
        log_config=True  # send to console (beware security of database URLs)
    )

    # with open("./config.yaml") as infile:
    #     config = AttrDict(yaml.safe_load(infile))
    #     config.port=DEFAULT_PORT

    validate(config)
    db = connect_to_db_using_attrdict(config.database_url)

    # Any additional user input required?
    # ask_user("Irrelevant: Heads or tails", default='H', options=['H', 'T'])

    # -------------------------------------------------------------------------
    # Set up task and go
    # -------------------------------------------------------------------------

    session = AttrDict(start=datetime.now(),
                       subject=config.subject,
                       session=config.session)
    insert_and_set_id(db[SESSION_TABLE], session)  # save to database
    log.info("Off we go...")
    task = VisualDiscriminationTask(config, db, session)
    task.connect(config.server, config.port)
  
    def shutdown():
        log.info("Storing Data")
        # -------------------------------------------------------------------------
        # Done. Calculate summaries. Save data from this session to new CSV files.
        # -------------------------------------------------------------------------

        # Retrieve all our trials. (There may also be many others in the database.)
        # NOTE that find() returns an iterator (you get to iterate through it ONCE).
        # Since we want to use this more than once (below), use a list.
        trials = list(db[TRIAL_TABLE].find(session_id=session.id))

        # Calculate some summary measures
        summary = AttrDict(
            session_id=session.id,  # foreign key
            date=datetime.utcnow(),
            trials=len(trials),
            trials_rewarded=sum(t.rewarded for t in trials),
        )
        insert_and_set_id(db[SUMMARY_TABLE], summary)  # save to database

        # Save data. (Since the session and summary objects are single objects, we
        # encapsulate them in a list.)
        save_data("session", [session], timestamp=session.start,
                  taskname=TASKNAME_SHORT)
        save_data("trial", trials, timestamp=session.start,
                  taskname=TASKNAME_SHORT)
        save_data("summary", [summary], timestamp=session.start,
                  taskname=TASKNAME_SHORT)

    reactor.addSystemEventTrigger('before', 'shutdown', shutdown)
    # noinspection PyUnresolvedReferences
    reactor.run()  # starts Twisted and thus network processing
    log.info("Finished.")
    shutdown()

if __name__ == '__main__':
    main()