import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np


class FourRoomsEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    # base actions:
    # down = 0
    # up = 1
    # right = 2
    # left = 3
    # press_button = 4

    def __init__(self):
        self.rows = None
        self.columns = None
        self.rooms_intersec = None
        self.action_space = None
        self.map = None
        self.current_agent_loc = None
        self.doors_loc = None
        self.buttons_loc = None
        self.directions = [[0, -1], [0, 1], [1, 0], [-1, 0]]
        self.action_space = spaces.Discrete(5)  # 5 base actions
        self.all_actions = [i for i in range(0, 5)]
        self.observation_space = None
        self.pressed_buttons = None
        self.default_reward = 0
        self.reset()

    def reset(self):
        self.pressed_buttons = []
        #self.rows = np.random.randint(low=10, high=20)
        #self.columns = np.random.randint(low=10, high=20)
        self.rows = 6
        self.columns = 6
        self.rooms_intersec = (np.random.randint(1, self.rows - 1), np.random.randint(1, self.columns - 1))
        self.doors_loc = [(np.random.randint(low=0, high=self.rooms_intersec[0]), self.rooms_intersec[1]),
                     (np.random.randint(low=self.rooms_intersec[0] + 1, high=self.rows), self.rooms_intersec[1]),
                     (self.rooms_intersec[0], np.random.randint(low=0, high=self.rooms_intersec[1])),
                     (self.rooms_intersec[0], np.random.randint(low=self.rooms_intersec[1] + 1, high=self.columns))]
        self.buttons_loc = [(np.random.randint(low=0, high=self.rooms_intersec[0]), np.random.randint(low=0, high=self.rooms_intersec[1])),
                       (np.random.randint(low=self.rooms_intersec[0] + 1, high=self.rows), np.random.randint(low=0, high=self.rooms_intersec[1])),
                       (np.random.randint(low=0, high=self.rooms_intersec[0]), np.random.randint(low=self.rooms_intersec[1] + 1, high=self.columns)),
                       (np.random.randint(low=self.rooms_intersec[0] + 1, high=self.rows), np.random.randint(low=self.rooms_intersec[1] + 1, high=self.columns))]
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.rows, self.columns), dtype=np.float32)
        valid_start_loc = False
        while not valid_start_loc:
            self.current_agent_loc = (np.random.randint(low=0, high=self.rows), np.random.randint(low=0, high=self.columns))
            if self.current_agent_loc[0] != self.rooms_intersec[0] and self.current_agent_loc[1] != self.rooms_intersec[1] \
                    and self.current_agent_loc not in self.buttons_loc:
                valid_start_loc = True
        self.map = np.zeros((self.rows, self.columns))
        # 0 = empty
        # -1 = wall
        # 1 = button-1
        # 2 = button-2
        # 3 = button-3
        # 4 = button-4
        # 5 = agent
        # agent and button overlap = agent + button
        for i in range(self.rows):
            for j in range(self.columns):
                if i == self.rooms_intersec[0] or j == self.rooms_intersec[1]:
                    if (i, j) not in self.doors_loc:
                        self.map[i, j] = -1
                for button_idx, button_loc in enumerate(self.buttons_loc):
                    if (i, j) == button_loc:
                        self.map[i, j] = button_idx + 1
                if (i, j) == self.current_agent_loc:
                    self.map[i, j] = 5
        return self.map

    def step(self, action):
        done = False
        reward = self.default_reward
        agent_loc = list(self.current_agent_loc)
        if action <= 3:  # movement action
            new_loc = tuple(agent_loc + self.directions[action])
            if new_loc[0] >= 0 and new_loc[0] < self.rows and new_loc[1] >= 0 and new_loc[1] < self.columns and \
                    self.map[new_loc[0], new_loc[1]] != -1:
                self.map[self.current_agent_loc[0], self.current_agent_loc[1]] -= 5
                self.current_agent_loc = new_loc
                self.map[self.current_agent_loc[0], self.current_agent_loc[1]] += 5
        else:
            for button_idx, button_loc in enumerate(self.buttons_loc):  # pressing a button
                if abs(agent_loc[0] - button_loc[0]) + abs(agent_loc[1] - button_loc[1]) == 1:  # agent is 1 block away from a button
                    self.pressed_buttons.append(button_idx)
                if len(self.pressed_buttons) == 4:  # end episode if all 4 buttons were pushed
                    done = True
                    reward = 1
                # for button_idx, button in enumerate(self.pressed_buttons): # check pressing order
                #     if button_idx != button:
                #         reward = 0
        return self.map, reward, done, {}

    def render(self, mode='human'):
        print(self.map)

