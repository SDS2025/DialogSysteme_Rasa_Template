# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet



# print("oha actions loaded ")

# class ActionWakeUpInBasement(Action):
#     def name(self) -> str:
#         return "action_wake_up_in_basement"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         dispatcher.utter_message(text="You wake up in a cold, dimly lit basement. There's a door and a table in the room. What do you do?")
#         return []

# class ActionInspectTable(Action):
#     def name(self) -> str:
#         return "action_inspect_table"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         # Check if the key has already been picked up
#         if tracker.get_slot("key_found"):
#             dispatcher.utter_message(text="The table is empty now.")
#         else:
#             dispatcher.utter_message(text="You find a small rusty key on the table.")
#             return [SlotSet("key_found", True)]
#         return []

# class ActionInspectDoor(Action):
#     def name(self) -> str:
#         return "action_inspect_door"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         dispatcher.utter_message(text="The door is old and sturdy, but it's locked. You'll need a key to open it.")
#         return []

# class ActionTryToUnlockDoor(Action):
#     def name(self) -> str:
#         return "action_try_to_unlock_door"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         # Check if the user has the key
#         has_key = tracker.get_slot("key_found")

#         if has_key:
#             dispatcher.utter_message(text="The door creaks open, and you step into a dark corridor.")
#             return [SlotSet("door_unlocked", True)]
#         else:
#             dispatcher.utter_message(text="The door is locked. It seems you need a key to open it.")
#             return []

# class ActionGoLeftInCorridor(Action):
#     def name(self) -> str:
#         return "action_go_left_in_corridor"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         dispatcher.utter_message(text="You reach a dead end and have to turn back.")
#         return []

# class ActionGoRightInCorridor(Action):
#     def name(self) -> str:
#         return "action_go_right_in_corridor"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         dispatcher.utter_message(text="You go right and find another door leading into a second room.")
#         return []


class ActionDefaultFallback(Action):

    def name(self) -> Text: 
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        dispatcher.utter_message(text="Please repeat your answer again. If it does not work, try phrasing it differently.")
        return []



class ActionInitialize(Action):

    def name(self) -> Text:
        return "action_initialize"
    

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.latest_message)

        if tracker.get_slot('game_data') is None or tracker.get_slot('game_data') == "null":
            game_data = {"has_key": False, "room": "start", "door1_open": False}
            
        else: game_data = tracker.get_slot('game_data')


        
        user_intent = tracker.latest_message['intent']['name']
        msg = "IDK ask someone else"
        
        if user_intent == 'greet':
            msg = "You wake in a dark room with no memory of how you got here. There is a door and a small table in the room with you."
            game_data['has_key']= False
        elif user_intent == 'inspect_table':
            if(game_data['has_key']):
                msg = "You already picked up the key, which seems to be the only relevant thing on this table."
            else:
                game_data['has_key']= True
                msg = "You look on the table. Between old books and dust, you find a key."
        elif user_intent == 'inspect_door':
            if(game_data['has_key']):
                msg = "You already found a key. Would you like to use it?"
            else:
                game_data['has_key']= True
                msg = "It seems like you would need a key to unlock this door."
        elif user_intent== 'unlock_door':
            if(game_data['has_key']& game_data['door1_open']==False):
                game_data['door1_open']= True
                msg = "You open the door and find yourself looking at an empty hallway. Do you wish to go left or right?"
            if(game_data['has_key']& game_data['door1_open']):
                msg = "You already opened the door and find yourself looking at an empty hallway once again. Do you wish to go left or right?"
            else:
                msg = "The door is still locked."
        elif user_intent=='go_left':
            msg = "You go to the left but find yourself facing a brick wall. You turn around and find yourself at the door you left through."        
        elif user_intent=='go_right':
            msg = "You go to the right and find a second door, which seems to be unlocked. You enter a second room."
            game_data['room']= "second"
        elif user_intent=='sleep':
            msg= "YOu go back to sleep and wake up to your normal room. It was all just a dream."

        dispatcher.utter_message(text=msg)

        return [SlotSet("game_data", game_data)]
