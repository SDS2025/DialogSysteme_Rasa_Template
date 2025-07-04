# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActionExecuted, UserUtteranceReverted


class ActionDefaultFallback(Action):

    def name(self) -> Text: 
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        dispatcher.utter_message(text="Please repeat your answer again. If it does not work, try phrasing it differently.")
        return [UserUtteranceReverted()]



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

        current_room = tracker.get_slot('current_room') or 'first_room'
        print(f'current_room: {current_room}')
        response = None
        # return [SlotSet("current_room", "library")]
        
        user_intent = tracker.latest_message['intent']['name']
        msg = "I did not catch that. Maybe try something else."

        has_key = game_data['has_key']  # type: bool

        if user_intent == 'inventory':
            if has_key:
                msg= "You have the following items: Key to an unknown lock"
            else:
                msg = "You have not picked up any items on your journey yet."

        if user_intent == 'greet':
            response = "utter_intro_other"

        if user_intent == 'inspect_table':
            if current_room == "first_room":
                if(has_key):
                    msg = "You already picked up the key, which seems to be the only relevant thing on this table."
                else:
                    has_key= True
                    # msg = "You look on the table. Between old books and dust, you find a key."
                    response = "utter_lookat_table"
            else:
                response = "utter_lookat_table"
        
        if game_data['room']=="start":
            if user_intent == 'greet':
                # msg = "You wake in a dark room with no memory of how you got here. There is a door and a small table in the room with you."
                # response = "utter_intro_other"
                has_key= False
            # elif user_intent == 'inspect_table':
            #     if(has_key):
            #         msg = "You already picked up the key, which seems to be the only relevant thing on this table."
            #     else:
            #         has_key= True
            #         # msg = "You look on the table. Between old books and dust, you find a key."
            #         response = "utter_lookat_table"
            elif user_intent == 'inspect_door':
                if(has_key):
                  msg = "You already found a key. Would you like to use it?"
                else:
                    msg = "It seems like you would need a key to unlock this door."
            elif user_intent== 'unlock_door':
                if(has_key& game_data['door1_open']==False):
                    msg = "You open the door and find yourself looking at an empty hallway. Do you wish to go left or right?"
                    game_data['door1_open']= True
                    current_room = 'hallway'
                if(has_key& game_data['door1_open']):
                    msg = "You open the door and find yourself looking at an empty hallway . Do you wish to go left or right?"
                else:
                    msg = "The door is still locked."
            elif user_intent=='go_left':
                # needs to check for key?
                msg = "You go to the left but find yourself facing a brick wall. You turn around and find yourself at the door you left through."        
            elif user_intent=='go_right':
                # needs to check for key?
                msg = "You go to the right and find a second door, which seems to be unlocked. You enter a second room."
                game_data['room']= "second"
                current_room = 'second_room'
            elif user_intent=='sleep':
                msg= "You go back to sleep and wake up to your normal room. It was all just a dream."
        elif game_data['room']=="second":
            if user_intent == 'inspect_door':
                # return [ActionExecuted("action_enter_code")]
                response = "utter_door_room2"

        game_data['has_key'] = has_key
        if response:
            dispatcher.utter_message(response=response)
        else:
            dispatcher.utter_message(text=msg)

        return [SlotSet("game_data", game_data), SlotSet("current_room", current_room)]
    

class ActionChooseBook(Action):
    def name(self) -> Text:
        return "action_choose_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        book = tracker.latest_message.get('text', '').lower()

        if "cooking" in book:
            dispatcher.utter_message(response="utter_cooking_book")
        elif "legends" in book:
            dispatcher.utter_message(response="utter_legends_book")
        elif "royal" in book:
            dispatcher.utter_message(response="utter_royal_book")
            return [SlotSet("knows_order", True)]
        else:
            dispatcher.utter_message(text="I couldn't find that book.")
        return []
    

class ActionMemory(Action):

    def name(self) -> Text:
        return "action_memory"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print(tracker.latest_message)

# Slot für Bücher
        selected_book = tracker.latest_message.get('text', '').strip()

        default_game_data2 = {
            "order": False,
            "door_lock": False,
            "painting east": False,
            "painting west": False,
            "painting north": False
        }

# Bestehenden Slot holen oder neues Dict starten
        game_data2 = tracker.get_slot('game_data2') or {}

# Fehlende Keys auffüllen
        for key, default in default_game_data2.items():
           game_data2.setdefault(key, default)
        
        user_intent = tracker.latest_message['intent']['name']
        knows_paintings = game_data2["painting east"] and game_data2["painting west"] and game_data2["painting north"]
        knows_order = game_data2["order"]
# Logik für Memory
        if user_intent == 'memory':
            if not knows_paintings:
                messages = []
                painting_info = {
                    "painting east": "King Alric - 4",
                    "painting west": "Prince Cedric - 2",
                    "painting north": "Queen Berena - 9"
                }
                for k,v in painting_info.items():
                    if game_data2[k]== True:
                        messages.append(v)
                dispatcher.utter_message(text=', '.join(messages))
                dispatcher.utter_message(response=knows_order and "utter_memory_book" or "utter_error")
            else:
                dispatcher.utter_message(response=knows_order and "utter_memory_lock" or "utter_memory_empty")

                    
                # if knows_order and knows_paintings:
                #     dispatcher.utter_message(response="utter_memory_lock")
                # elif knows_order== True:
                #     dispatcher.utter_message(response="utter_memory_book")
                # elif not (knows_order and knows_paintings):
                #     dispatcher.utter_message(response="utter_memory_empty")
                # else:
                #     dispatcher.utter_message(response="utter_error")    



            # if knows_paintings and not game_data2["order"]:
            #     dispatcher.utter_message(response="utter_code_numbers")
            # elif game_data2["order"] and knows_paintings:
            #     dispatcher.utter_message(response="utter_memory_lock")
            # elif game_data2["order"]== True:
            #     dispatcher.utter_message(response="utter_memory_book")
            # elif game_data2["painting east"]== True:
            #     dispatcher.utter_message(text="King Alric - 4")
            # elif game_data2["painting west"]== True:
            #     dispatcher.utter_message(text="Prince Cedric - 2")
            # elif game_data2["painting north"]== True:
            #     dispatcher.utter_message(text="Queen Berena - 9")
            # elif game_data2["painting east"] and game_data2["painting west"]:
            #     dispatcher.utter_message(text="King Alric - 4\n Prince Cedric - 2")
            # elif game_data2["painting east"] and game_data2["painting north"]:
            #     dispatcher.utter_message(text="King Alric - 4\n Queen Berena - 9")
            # elif game_data2["painting west"] and game_data2["painting north"]:
            #     dispatcher.utter_message(text="Queen Berena - 9\nPrince Cedric - 2")
            # elif not (game_data2["order"] and knows_paintings):
            #     dispatcher.utter_message(response="utter_memory_empty")
            # else:
            #     dispatcher.utter_message(response="utter_error")      
 # Logik für Bücher
        elif user_intent == 'Cooking_book':
            dispatcher.utter_message(response="utter_cooking_book")
        elif user_intent == 'Legends_book':
            dispatcher.utter_message(response="utter_legends_book")
        elif user_intent == 'Royal_book':
            dispatcher.utter_message(response="utter_royal_book")
            game_data2['order'] = True

        # Logik für Gemälde
        elif user_intent == 'painting_east':
            dispatcher.utter_message(response="utter_painting_east")
            game_data2['painting east'] = True
        elif user_intent == 'painting_west':
            dispatcher.utter_message(response="utter_painting_west")
            game_data2['painting west'] = True
        elif user_intent == 'painting_north':
            dispatcher.utter_message(response="utter_painting_north")
            game_data2['painting north'] = True

        # Wenn kein Intent gematcht wurde
        else:
            dispatcher.utter_message(text="I couldn't find that book.")

        return [SlotSet("game_data2", game_data2)]
       

class ActionEnterCode(Action):
    def name(self) -> Text:
        return "action_enter_code"

    def get_code_parts(self, code: str) -> list[int]:
        code_l = list(code)
        try:
            code_l = [int(x) for x in code_l]
        except Exception as ex:
            print(f'get_code_parts exception: {ex}') # hm maybe not just throw an ex
        return code_l


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        correct_code = "492" # this could be randomized
        code = next(tracker.get_latest_entity_values("code"), None)
        correct_code_l = self.get_code_parts(correct_code)
        code_l = self.get_code_parts(code)
        permut = all([c in code_l for c in correct_code_l])
        # print('permut', [c in code_l for c in correct_code_l])

        if code == correct_code:
            dispatcher.utter_message(response="utter_code_success")
            return [SlotSet("current_room", "freedom")]
        else:
            if len(set(code_l)) == 1:
                dispatcher.utter_message(response="utter_too_easy")
            if permut:
                dispatcher.utter_message(response="utter_code_wrong_order")
            else:
                dispatcher.utter_message(response="utter_code_wrong", code=code)

        # text = tracker.latest_message.get('text', '')
        # if "492" in text or "4 9 2" in text:
        #     dispatcher.utter_message(response="utter_code_success")
        #     return [SlotSet("current_room", "freedom")]
        # elif "4" in text and "9" in text and "2" in text:
        #     dispatcher.utter_message(response="utter_code_wrong_order")
        # else:
        #     dispatcher.utter_message(response="utter_code_wrong")
        return []
    
class ActionRecallMemory(Action):
    def name(self) -> Text:
        return "action_recall_memory"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        mem_text = []
        if tracker.get_slot("mem_east"):
            mem_text.append("King Alric - 4")
        if tracker.get_slot("mem_north"):
            mem_text.append("Queen Berena - 9")
        if tracker.get_slot("mem_west"):
            mem_text.append("Prince Cedric - 2")

        if mem_text:
            dispatcher.utter_message(response="utter_memory_recall")
            for line in mem_text:
                dispatcher.utter_message(text=line)
        else:
            dispatcher.utter_message(response="utter_memory_empty")
        return []
