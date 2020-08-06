import os
import matplotlib.pyplot as plt
import gym
import gym_random_rooms

from stable_baselines import PPO2

from action_filters import PPOGrammarFilter, PPOAllPassFilter

import numpy as np
import tensorflow as tf
from stable_baselines.a2c.utils import conv, linear, conv_to_fc, lstm
from stable_baselines.deepq.policies import FeedForwardPolicy


if __name__ == '__main__':
    time_steps = 300000
    env = gym.make('random_rooms-v0', max_steps=100, rows=8, cols=14, upsample=4, key_reward=0.1, door_reward=0.1, doors_num=4, same_places=True, bundle_doors=True, master_key=True, n_inner_resets=1, inner_counter_in_state=False, seed=8)
    #env = gym.make('Freeway-v0')
    #env = gym.make('MiniGrid-Empty-8x8-v0')

    log_dir = "./log/"
    log_name = "DoorKey_rows8_cols14_steps100_keydoorreward01_doors4_sameplaces_chginitialstate_masterkey_GrammarHistory60Penalty005_penaltyNclean"
    #log_name = "DoorKey_rows8_cols14_steps100_keydoorreward01_doors4_sameplaces_chginitialstate_masterkey_SB"

    def checkpoints(episode_id):
        return episode_id % 50 == 0

    prev_runs = [0] + [int(dir.split('_')[-1]) for dir in os.listdir(log_dir) if dir.startswith(log_name)]
    env = gym.wrappers.Monitor(env, "./videos/" + log_name + str(max(prev_runs) + 1), video_callable=checkpoints, force=True)
    env.reset()

    #model = DQN('CnnPolicy', env, exploration_final_eps=0.02, learning_rate=2e-4, batch_size=128, target_network_update_freq=1500, exploration_fraction=0.35, verbose=1, tensorboard_log=log_dir, filter=AllPassFilter(), grammar_on_exploration=True)

    model = PPO2('CnnPolicy', env, tensorboard_log=log_dir, filter=PPOGrammarFilter(history_size=60, negate_grammar=False, grammar_file="grammar.txt"), grammar_penalty=0.05)
    # model = PPO2('CnnPolicy', env, tensorboard_log=log_dir)
    model.learn(total_timesteps=time_steps, tb_log_name=log_name)
    env.close()

