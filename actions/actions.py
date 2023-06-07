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



print("oha actions loaded ")
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"
    


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.latest_message)

        if tracker.get_slot('data') is None or tracker.get_slot('data') == "null":
            data = {"has_key": False, "room": "start"}
            
        else: data = tracker.get_slot('data')



        user_intent = tracker.latest_message['intent']['name']
        msg = "IDK ask someone else"
        
        if user_intent == 'greet':
            msg = "Hello there, give me your key (if you have any)"
            data['has_key']= False
        elif user_intent == 'door_3':
            msg = "You open the door and find a key"
            data['has_key']= True
        elif user_intent== 'door_1':
            if(data['has_key']):
                msg = "You open the door and escape"
            else:
                msg = "The door is verschlossen"
        

        dispatcher.utter_message(text=msg)

        return [SlotSet("data", data)]
