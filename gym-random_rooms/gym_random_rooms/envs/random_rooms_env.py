import numpy as np
from random import sample, uniform
import gym
from gym import error, core, spaces, utils
from gym.envs.registration import register
from gym.utils import seeding
import cv2
import matplotlib.pyplot as plt

# actions = 0:null, 1:up, 2:down, 3:left, 4:right, 5:pick, 6...: toggle some door

# define colors
COLORS = {'black': [0.0, 0.0, 0.0], 'gray': [0.5, 0.5, 0.5],
          'blue': [0.0, 0.0, 1.0], 'green': [0.0, 1.0, 0.0],
          'red': [1.0, 0.0, 0.0], 'pink': [1.0, 0.0, 1.0],
          'yellow': [1.0, 1.0, 0.0], 'white': [1.0, 1.0, 1.0]}


class RandomRoomsEnv(gym.Env):  # instead of core.Env
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 1
    }

    def __init__(self,
                 cols=20,
                 rows=5,
                 doors_num=3,
                 upsample=10,
                 max_steps=30,
                 key_reward=0.0,
                 door_reward=0.0,
                 n_inner_resets=1000,
                 inner_counter_in_state=True,
                 same_places=True,
                 bundle_doors=False,
                 master_key=False,
                 seed=None):

        self.rows = rows + 2
        self.cols = cols + 2
        self.keys_num = 1 if master_key else doors_num
        self.doors_num = doors_num
        self.upsample = upsample
        self.max_steps = max_steps
        self.same_places = same_places
        self.master_key = master_key
        self.key_reward = key_reward
        self.door_reward = door_reward

        # if 2*self.keys_num + 2 > self.rows:
        #     raise Exception("Board is too small")

        self.counter = 0
        self.n_inner_resets = n_inner_resets
        self.inner_counter_in_state = inner_counter_in_state
        self.bundle_doors = bundle_doors
        n_channels = 3 + inner_counter_in_state  # map + state + goal
        if self.bundle_doors:
            n_channels += 1
        else:
            n_channels += self.doors_num
        if self.master_key:
            n_channels += 1
        else:
            n_channels += self.keys_num

        # self.null_action = null_action
        # self.action_space = spaces.Discrete(5 + int(self.null_action) + self.doors_num)
        self.action_space = spaces.Discrete(5 + self.doors_num)

        self.observation_space = spaces.Box(low=0, high=1,
                                            shape=(self.rows * self.upsample, self.cols * self.upsample, n_channels),
                                            dtype=np.float32)

        self.directions = [np.array((-1, 0)), np.array((1, 0)), np.array((0, -1)), np.array((0, 1))]

        self.rng = np.random.RandomState(seed)

        self.map, self.doors_cells, self.doors, self.keys_cells, self.keys = self._randomize_walls()

        self.goal_cell = np.array((self.rows - 2, self.cols - 2))
        self.goal = np.zeros_like(self.map)
        self.goal[self.goal_cell[0] * self.upsample:(self.goal_cell[0] + 1) * self.upsample,
        self.goal_cell[1] * self.upsample:(self.goal_cell[1] + 1) * self.upsample] = 1
        self.state_cell = np.array((1, 1))
        self.state = np.zeros_like(self.map)
        self.state[self.state_cell[1] * self.upsample:(self.state_cell[1] + 1) * self.upsample,
        self.state_cell[1] * self.upsample:(self.state_cell[1] + 1) * self.upsample] = 1

        self.keys_on = [False for _ in range(self.keys_num)]
        self.doors_open = [False for _ in range(self.doors_num)]

        self.nsteps = 0
        self.tot_reward = 0

    def reset(self, override=False, hard=False):

        # self.counter += 1
        # if self.counter >= self.n_inner_resets:
        #    print('FINAL RESET with reward: {}'.format(self.tot_reward))
        #    # self.init_values = self.map, self.doors_cells, self.doors,  self.keys_cells, self.keys = self._randomize_walls()
        #    self.map, self.doors_cells, self.doors,  self.keys_cells, self.keys = self._randomize_walls() # NKAM
        #    self.counter = 0

        # restore values or new ones
        self.counter += 1
        if self.same_places:
            self.map, self.doors, self.keys = self._doorskeys(keys_cells=self.keys_cells, doors_cells=self.doors_cells,
                                                              map=self.map)
        elif self.counter >= self.n_inner_resets:
            self.map, self.doors_cells, self.doors, self.keys_cells, self.keys = self._randomize_walls()  # NKAM
            self.counter = 0

        self.goal_cell = np.array((self.rows - 2, self.cols - 2))
        self.goal = np.zeros_like(self.map)
        self.goal[self.goal_cell[0] * self.upsample:(self.goal_cell[0] + 1) * self.upsample,
        self.goal_cell[1] * self.upsample:(self.goal_cell[1] + 1) * self.upsample] = 1
        # self.state_cell = np.array((1, 1))
        left_most_door = min([cell[1] for cell in self.doors_cells])
        if left_most_door <= 2:
            left_most_door = 3
        self.state_cell = np.array((np.random.randint(1, self.rows - 2), np.random.randint(1, left_most_door - 1)))

        self.state = np.zeros_like(self.map)
        self.state[self.state_cell[1] * self.upsample:(self.state_cell[1] + 1) * self.upsample,
        self.state_cell[1] * self.upsample:(self.state_cell[1] + 1) * self.upsample] = 1

        self.keys_on = [False for _ in range(self.keys_num)]
        self.doors_open = [False for _ in range(self.doors_num)]

        self.nsteps = 0
        self.tot_reward = 0
        obs = self._im_from_state()
        return obs

    def step(self, action):
        r = 0.0
        # r = -(0.05 / self.max_steps)

        if 0 <= action <= 3:
            next_cell = self.state_cell + self.directions[action]
            if self.map[next_cell[0] * self.upsample, next_cell[1] * self.upsample] == 0:
                self.state_cell = next_cell
                self.state = np.zeros_like(self.map)
                self.state[self.state_cell[0] * self.upsample:(self.state_cell[0] + 1) * self.upsample,
                self.state_cell[1] * self.upsample:(self.state_cell[1] + 1) * self.upsample] = 1

        elif action == 4:
            # pick
            for i in range(self.keys_num):
                if np.all(self.state_cell == self.keys_cells[i]) and not self.keys_on[i]:
                    r += self.key_reward
                    self.keys_on[i] = True
                    self.keys[i] = np.zeros_like(self.map)

        elif action >= 5:
            # toggle
            current_door = action - 5
            # if np.all(self.state_cell + self.directions[3] == self.doors_cells[current_door]) and self.keys_on[current_door] and not self.doors_open[current_door]:
            if np.all(self.state_cell + self.directions[3] == self.doors_cells[current_door]) and not self.doors_open[
                current_door]:
                if (self.master_key and self.keys_on[0]) or ((not self.master_key) and self.keys_on[current_door]):
                    self.doors_open[current_door] = True
                    if all(self.doors_open):
                        r += self.door_reward
                        # COLORS['blue'] = [1, 0, 0]
                    self.doors[current_door] = np.zeros_like(self.map)
                    self.map[self.doors_cells[current_door][0] * self.upsample:(self.doors_cells[current_door][
                                                                                    0] + 1) * self.upsample,
                    self.doors_cells[current_door][1] * self.upsample:(self.doors_cells[current_door][
                                                                           1] + 1) * self.upsample] = 0

        done = np.all(self.state_cell == self.goal_cell)
        if done:
            r += (1 - (self.key_reward + self.door_reward))
            # COLORS['blue'] = [0, 1, 1]
        obs = self._im_from_state()

        if self.nsteps >= self.max_steps:
            done = True

        self.tot_reward += r
        self.nsteps += 1
        info = dict()
        if done:
            info['episode'] = {'r': self.tot_reward, 'l': self.nsteps}

        # print(self.get_pseudo_state())
        return obs, r, done, info

    def _im_from_state(self):
        im_list = [self.state, self.map, self.goal]
        for i in range(self.keys_num):
            im_list.append(self.keys[i])

        if self.bundle_doors:
            all_doors = np.zeros_like(self.map)
            for i in range(self.doors_num):
                all_doors += self.doors[i]
            im_list.append(all_doors)
        else:
            for i in range(self.doors_num):
                im_list.append(self.doors[i])

        if self.inner_counter_in_state:
            im_list.append((self.counter / self.n_inner_resets) * np.ones_like(self.map))
        return np.stack(im_list, axis=-1)

    def _doorskeys(self, keys_cells, doors_cells, map):
        doors = []
        keys = []
        for i in range(self.doors_num):
            current_door = np.zeros_like(map)
            current_door[(doors_cells[i][0]) * self.upsample:(doors_cells[i][0] + 1) * self.upsample,
            (doors_cells[i][1]) * self.upsample:(doors_cells[i][1] + 1) * self.upsample] = 1
            doors.append(current_door)
            map[:, (doors_cells[i][1]) * self.upsample:(doors_cells[i][1] + 1) * self.upsample] = 1

        for i in range(self.keys_num):
            current_key = np.zeros_like(map)
            current_key[(keys_cells[i][0]) * self.upsample:(keys_cells[i][0] + 1) * self.upsample,
            (keys_cells[i][1]) * self.upsample:(keys_cells[i][1] + 1) * self.upsample] = 1
            keys.append(current_key)
        return map, doors, keys

    def _randomize_walls(self):
        map = np.zeros((self.rows * self.upsample, self.cols * self.upsample))

        map[0:self.upsample, :] = 1
        map[:, 0:self.upsample] = 1
        map[-self.upsample:, :] = 1
        map[:, -self.upsample:] = 1

        doors_cells = []
        if self.bundle_doors:
            first_door_col = self.rng.randint(2 + self.keys_num, self.cols - 2 - self.doors_num + 1)
            doors_row = self.rng.randint(2, self.rows - 2)
            for i in range(self.doors_num):
                doors_cells.append(np.array((doors_row, first_door_col + i)))
        else:
            doors_cols = self.rng.choice(range(2 + self.keys_num, self.cols - 2), self.doors_num, replace=False)
            first_door_col = min(doors_cols)
            for i in range(self.doors_num):
                row = self.rng.randint(2, self.rows - 2)
                if i != 0:
                    for j in range(i):
                        if doors_cols[i] == doors_cols[j] + 1 or doors_cols[i] == doors_cols[j] - 1:
                            row = doors_cells[j][0]
                doors_cells.append(np.array((row, doors_cols[i])))

        keys_cells = []
        keys_cols = self.rng.choice(range(2, first_door_col), self.keys_num, replace=False)
        for i in range(self.keys_num):
            keys_cells.append(np.array((self.rng.randint(2, self.rows - 2), keys_cols[i])))

        map, doors, keys = self._doorskeys(keys_cells, doors_cells, map)

        return map, doors_cells, doors, keys_cells, keys

    def _gridmap_to_observation(self):
        observation = np.zeros((self.map.shape[0], self.map.shape[1], 3))
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                observation[i, j] = np.array(COLORS['white'])

        # walls
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                if self.map[i, j]:
                    observation[i, j] = np.array(COLORS['black'])
        # state
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                if self.state[i, j]:
                    observation[i, j] = np.array(COLORS['blue'])
        # goal
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                if self.goal[i, j]:
                    observation[i, j] = np.array(COLORS['green'])

        possible_colors = [COLORS['yellow'], COLORS['pink'], COLORS['red'], COLORS['gray']]
        # doors and keys
        for i in range(self.doors_num):
            if self.doors_num <= 4:
                door_color = possible_colors[i]
            else:
                door_color = COLORS['gray']
            # color = [uniform(0, 1), uniform(0, 1), uniform(0, 1)]
            # door
            for j in range(self.map.shape[0]):
                for k in range(self.map.shape[1]):
                    if self.doors[i][j, k]:
                        observation[j, k] = np.array(door_color)
                        # if door is closed it will override the black assignment of walls

        for i in range(self.keys_num):
            if self.keys_num <= 4:
                key_color = possible_colors[i]
            else:
                key_color = COLORS['yellow']
            # color = [uniform(0, 1), uniform(0, 1), uniform(0, 1)]
            # key
            for j in range(self.map.shape[0]):
                for k in range(self.map.shape[1]):
                    if self.keys[i][j, k]:
                        observation[j, k] = np.array(key_color)
        observation *= 255
        return observation.astype('uint8')

    def render(self, mode='human', close=False):
        img = self._gridmap_to_observation()
        return img

    def get_pseudo_state(self):
        if all(self.doors_open):
            return 2
        if all(self.keys_on):
            return 1
        return 0
        # possible_states = ["need to pick", "need to open doors", "need to go to goal"]


if __name__ == '__main__':
    env = RandomRoomsEnv()
    obs = env.reset()
    plt.imshow(obs)
    plt.show()