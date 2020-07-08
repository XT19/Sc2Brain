import time

from pysc2.agents import base_agent #Importation des elements de Starcraft 2
from pysc2.env import sc2_env
from pysc2.lib import actions,features,units
from absl import app
import random

class PyAgent(base_agent.BaseAgent):
    def step(self, obs):
        super(PyAgent,self).step(obs)
        #time.sleep(0.2)

        if self.buildSupplyDepot(obs):#Lance la methode de verification de la reserve
            x = random.randint(15,83)
            y = random.randint(15,83)
            return  actions.FUNCTIONS.Build_SupplyDepot_screen('now', (x, y))
        if self.buildBarracks(obs):#Lance la methode de verification de la reserve
            x = random.randint(25,83)
            y = random.randint(25,83)
            return  actions.FUNCTIONS.Build_Barracks_screen('now', (x, y))
        if self.buildMarines(obs):
            return  actions.FUNCTIONS.Train_Marine_quick('now')
        if self.attack(obs):
            return  actions.FUNCTIONS.Attack_minimap(0, [19, 23])

#################################SELECTION###############################################
        marines = self.get_units_by_type(obs, units.Terran.Marine)
        if len(marines) > 6:
            marine = random.choice(marines)
            return actions.FUNCTIONS.select_point("select_all_type", (marine.x, marine.y))

        barracks = self.get_units_by_type(obs, units.Terran.Barracks)
        if len(barracks) > 0:
            barrack = random.choice(barracks)
            return  actions.FUNCTIONS.select_point("select_all_type", (barrack.x, barrack.y))

        VCS = self.get_units_by_type(obs, units.Terran.SCV)#Selection de tout les VCS
        if len(VCS) > 0:
            drone = random.choice(VCS)
            return  actions.FUNCTIONS.select_point("select_all_type",(drone.x, drone.y))

        return  actions.FUNCTIONS.no_op() #L'action a faire

#############################################################################################

    def buildSupplyDepot(self,obs):
        supplyDepots = self.get_units_by_type(obs, units.Terran.SupplyDepot)
        if len(supplyDepots) < 3:#Verifie si on a pas la reserve et la construit
            if self.unit_type_is_selected(obs, units.Terran.SCV):#Verifie si on a selectioné le VCS
                if(actions.FUNCTIONS.Build_SupplyDepot_screen.id in #Verifie si on est capable de la construire
                    obs.observation.available_actions):
                    return  True
                return  False

    def buildBarracks(self,obs):
        barracks = self.get_units_by_type(obs, units.Terran.Barracks)#Les barracks observè
        if len(barracks) < 2:#Verifie si on a pas la barracks et la construit
            if self.unit_type_is_selected(obs, units.Terran.SCV):#Verifie si on a selectioné le VCS
                if(actions.FUNCTIONS.Build_Barracks_screen.id in #Verifie si on est capable de la construire
                    obs.observation.available_actions):
                    return  True
                return  False

    def buildMarines(self,obs):
        marine = self.get_units_by_type(obs, units.Terran.Marine)#Les marines observè
        if len(marine) <= 8:
            if self.unit_type_is_selected(obs, units.Terran.Barracks):
                if(actions.FUNCTIONS.Train_Marine_quick.id in obs.observation.available_actions):#Verifie si la formation de marines est possible
                    return True
                return False

    def attack(self,obs):
        marine = self.get_units_by_type(obs, units.Terran.Marine)#Les marines observè
        if len(marine) <= 6:
            if self.unit_type_is_selected(obs, units.Terran.Marine):
                if(actions.FUNCTIONS.Attack_screen.id in obs.observation.available_actions):#Verifie si la formation de marines est possible
                    return True
                return False

    def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and
                obs.observation.single_select[0].unit_type == unit_type):
            return True
        if (len(obs.observation.multi_select) > 0 and
                obs.observation.multi_select[0].unit_type == unit_type):
            return True
        return False


    def get_units_by_type(self, obs, unit_type):#Selection de tout les unites par type
        return [unit for unit in obs.observation['feature_units']
                if unit.unit_type == unit_type
                and unit.alliance == features.PlayerRelative.SELF]


def main(argv):
    agent = PyAgent()
    try:
        while True:
            with sc2_env.SC2Env(
                map_name="Simple64",#La map qu'on va utiliser
                    players = [sc2_env.Agent(sc2_env.Race.terran), #La race qu'on va jouer
                               sc2_env.Bot(sc2_env.Race.random , sc2_env.Difficulty.very_easy)], #Le bot contre le quel on va jouer
                agent_interface_format=features.AgentInterfaceFormat(
                    feature_dimensions=features.Dimensions(screen=84, minimap=64),#Taille de l'interface du visualiseur
                    use_feature_units=True),
                step_mul=8, #Actions par minutes (qui ici est la moyenne)
                game_steps_per_episode=0,
                visualize=True) as env:
                agent.setup(env.observation_spec(), env.action_spec())#Observation des actions possible

                timesteps = env.reset()
                agent.reset()

                while True:
                    step_actions = [agent.step(timesteps[0])]
                    if timesteps[0].last():#Si il ne y'a plus d'actions a faire
                        break
                    timesteps = env.step(step_actions)
    except KeyboardInterrupt:
        pass


if __name__=="__main__":
    app.run(main)