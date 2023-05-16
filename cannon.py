import time
import random
import utilities.api.item_ids as ids
import utilities.color as clr
from utilities.color import Color

import utilities.ocr as ocr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
import utilities.imagesearch as imsearch
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import Point, Rectangle

class OSRSCannon(OSRSBot):
    def __init__(self):
        bot_title = "Auto Cannon"
        description = "Option for prayer potions and food"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 1
        self.prayer_on = False
        self.food_on = False
        self.cannon_on = False
        self.fighter_on = False
        self.prayer_random_chance = rd.random.randint(25,60) / 100
        self.last_npc_hitpoins = 0

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_slider_option("min_cannonballs", "Min cannonballs before click?", 1, 50)
        self.options_builder.add_slider_option("max_cannonballs", "Max cannonballs before click?", 1, 50)
        self.options_builder.add_checkbox_option("combat_types", "Which types?", ["Cannon", "Food", "Prayer"])
        self.options_builder.add_dropdown_option("food","What food to eat?",["None","Lobster","Shark","Manta_ray","Anglerfish"])
        # self.options_builder.add_text_edit_option("drops","Drops you want to pick up. A list seperated by a comma for each item","Coins,Tokkul")
   
    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            print(options)
            if option == "running_time":
                self.running_time = options[option]
            elif option == "combat_types":


                if 'Prayer' in options[option]:
                    self.prayer_on = True
                if 'Food' in options[option]:
                    self.food_on = True
                if 'Cannon' in options[option]:
                    self.cannon_on = True
                if 'Fighter' in options[option]:
                    self.fighter_on = True

            elif option == "min_cannonballs":
                self.min_cannonballs = options[option]

            elif option == "max_cannonballs":
                self.max_cannonballs = options[option]

            elif option == "food":
                self.food = options[option]

            elif option == "drops":
                lst = []
                if  options[option]:
                    lst = options[option].split(",")
                self.drop_list = lst
          
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Cannonballs refill between: {self.min_cannonballs} and { self.max_cannonballs}.")
        self.log_msg(f"Food: {self.food}")
        self.log_msg(f"Drops: {self.drop_list}.")

        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. To see what the APIs can offer you, see here: https://github.com/kelltom/OSRS-Bot-COLOR/tree/main/src/utilities/api.
          For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.` operator to access their
          functions.
        """
        # Setup APIs
        self.api_m = MorgHTTPSocket()
        # self.api_s = StatusSocket()

        self.cannon_x=(self.win.game_view.get_top_left()[0])
        self.cannon_y=(self.win.game_view.get_top_left()[1])
        # clr.SOMETHING_YELLOW =
        self.new_yellow  = Color([255, 200, 0])
        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        self.fill_at = random.randint(self.min_cannonballs,self.max_cannonballs)
        self.log_msg("Fill cannon at "+ str(self.fill_at))
        while time.time() - start_time < end_time:
        
            
            if self.cannon_on:
                self.handle_cannon()

            if self.food_on:
                self.handle_food()

            if self.prayer_on:
                self.handle_prayer()

            # if self.fighter_on:
            #     self.handle_fighter()


            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop

    def handle_fighter(self):

       
        if (self.api_m.get_is_in_combat()):
            
            self.last_npc_hitpoins = self.api_m.get_npc_hitpoints()

            return True
       
        # if self.last_npc_hitpoins > 3:
        #     self.take_break(1,3)
        #     if (self.api_m.get_is_in_combat()):
        #         self.last_npc_hitpoins = self.api_m.get_npc_hitpoints()
        #         return True
        # self.take_break(2,3)

        if (self.pick_up_loot( self.drop_list )):
            self.take_break(1,2)

        tries = 0
        while self.api_m.get_npc_hitpoints() < 1:
            if enemy := self.get_nearest_tag(clr.PURPLE):
                self.mouse.move_to(enemy.random_point(),)
                if not self.mouseover_text(contains="Attack"):
                    continue
                self.mouse.click()
                time.sleep(3)
            time.sleep(1)
            tries = tries + 1
            if tries > 5:
                return
      
        self.log_msg("Found enemy")

       

    def handle_cannon(self):

        cannonballrect = Rectangle(left=self.cannon_x, top=self.cannon_y, width=100, height=200)
        extracted = ocr.extract_text(cannonballrect,ocr.PLAIN_12,[clr.RED, self.new_yellow,clr.GREEN])

        if extracted:
            if int(extracted) < self.fill_at:

                self.log_msg("Need to fill cannon")
                tries = 0
                found = True

                while not self.mouseover_text(contains="Fire"):
                    found = False
                    tries = tries + 1
                    
                    cannon = self.get_nearest_tag(clr.BLUE)
                    if cannon:
                        self.mouse.move_to(cannon.random_point(), mouseSpeed="fastest")
                        found = True
                    if tries > 10:
                        self.log_msg("Failed refilling")
                        found = False
                        break
                    time.sleep(1/2)

                if found:
                    self.fill_at = random.randint(self.min_cannonballs,self.max_cannonballs)
                    self.log_msg("Fill cannon at "+ str(self.fill_at))
                    self.mouse.click()
                    time.sleep(3)
           

        broken_cannon = self.get_nearest_tag(clr.CYAN)
        if broken_cannon:
            tries = 0
            found = True
            self.mouse.move_to(broken_cannon.random_point(), mouseSpeed="fastest")
            while not self.mouseover_text(contains="Repair"):
                found = False
                tries = tries + 1
                broken_cannon = self.get_nearest_tag(clr.CYAN)
                if cannon:
                    self.log_msg("Cannon needs repairing")
                    self.mouse.move_to(broken_cannon.random_point(), mouseSpeed="fastest")
                    found = True
                if tries > 10:
                    
                    break
                time.sleep(1/2)

            if found:
                self.mouse.click()
                self.fill_at = random.randint(self.min_cannonballs,self.max_cannonballs)
                repair_cannon = self.get_nearest_tag(clr.CYAN)
                while not repair_cannon:
                    tries = tries + 1
                    repair_cannon = self.get_nearest_tag(clr.CYAN)
                    if cannon:
                        self.log_msg("Cannon repaired")
                        self.mouse.move_to(cannon.random_point(), mouseSpeed="fastest")
                        break
                    if tries > 20:
              
                        break
                    time.sleep(1/2)

    def handle_food(self):
        while self.get_hp() < (self.api_m.get_skill_level("Hitpoints") * 0.8):
          
            shark_img = imsearch.BOT_IMAGES.joinpath("quberto_cannon_bot", self.food + ".png")
            if shark := imsearch.search_img_in_rect(shark_img, self.win.control_panel):
                self.mouse.move_to(shark.random_point(), mouseSpeed="fastest")
                self.mouse.click()
                self.log_msg("Eating: " + self.food )
            else:
                self.log_msg("no " + self.food + " left")
                break
            time.sleep(2)

    def handle_prayer(self):
        while self.get_prayer() < (self.api_m.get_skill_level("Prayer") * self.prayer_random_chance):
            msg = "Random chance was: " + str(self.prayer_random_chance* 100) + "%"
            self.log_msg(msg)
            self.prayer_random_chance = rd.random.randint(25,60) / 100
            msg = "new random chance is: " + str(self.prayer_random_chance * 100) + "%"
            self.log_msg(msg)
            if self.drink_potion(1):
                self.log_msg('Drank from prayer potion(1)')
                self.take_break(1,2)
                return True
            if self.drink_potion(2):
                self.log_msg('Drank from prayer potion(2)')
                self.take_break(1,2)
                return True
            if self.drink_potion(3):
                self.log_msg('Drank from prayer potion(3)')
                self.take_break(1,2)
                return True
            if self.drink_potion(4):
                self.log_msg('Drank from prayer potion(4)')
                self.take_break(1,2)
                return True
            self.log_msg('Failed to drink potion')
            return False
        
        return True

    def drink_potion(self,dose=1):
        name = "Prayer_potion("+str(dose)+")"
        potion_img = imsearch.BOT_IMAGES.joinpath("quberto_cannon_bot", name + ".png")
        if potion := imsearch.search_img_in_rect(potion_img, self.win.control_panel,confidence=0.02):
            self.mouse.move_to(potion.random_point(), mouseSpeed="fastest")
            self.mouse.click()
            return True
        return False


