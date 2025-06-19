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
            game_data = {"has_key": False, "room": "start"}
            
        else: game_data = tracker.get_slot('game_data')


        
        user_intent = tracker.latest_message['intent']['name']
        msg = "IDK ask someone else"
        
        if user_intent == 'greet':
            msg = "Hello there, give me your key (if you have any)"
            game_data['has_key']= False
        elif user_intent == 'door_3':
            msg = "You open the door and find a key"
            game_data['has_key']= True
        elif user_intent== 'door_1':
            if(game_data['has_key']):
                msg = "You open the door and escape"
            else:
                msg = "The door is verschlossen"
        

        dispatcher.utter_message(text=msg)

        return [SlotSet("game_data", game_data)]
