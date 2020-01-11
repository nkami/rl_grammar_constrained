from stable_baselines_master.stable_baselines import DQN
import gym
#import gym_minigrid
#from gym_minigrid.wrappers import *
from action_filters import GrammarFilter, AllPassFilter


if __name__ == '__main__':
    time_steps = 5000

    # env_name = 'MiniGrid-FourRooms-v0'
    # env = gym.make(env_name)
    # env = RGBImgPartialObsWrapper(env)
    # env = ImgObsWrapper(env)

    env = gym.make('CartPole-v1')
    log_dir = "./log/"

    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, filter=GrammarFilter())
    # model.learn(total_timesteps=time_steps, tb_log_name="MiniGrid-FourRooms-v0 : AllPassFilter")
    model.learn(total_timesteps=time_steps)


