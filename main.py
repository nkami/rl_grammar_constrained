import gym
from stable_baselines_master.stable_baselines import DQN
from stable_baselines_master.stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines_master.stable_baselines.deepq.policies import MlpPolicy
from stable_baselines_master.stable_baselines.bench import Monitor
from gym_four_rooms.envs.four_rooms_env import FourRoomsEnv
from action_filters import GrammarFilter, AllPassFilter


if __name__ == '__main__':
    time_steps = 100000

    # env_name = 'MiniGrid-FourRooms-v0'
    # env = gym.make(env_name)
    # env = RGBImgPartialObsWrapper(env)
    # env = ImgObsWrapper(env)

    env = FourRoomsEnv()
    env = Monitor(env, filename=None, allow_early_resets=True)
    env = DummyVecEnv([lambda: env])


    log_dir = "./log/"

    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, filter=GrammarFilter())
    model.learn(total_timesteps=time_steps, tb_log_name="Four Rooms: Grammar")
    # model.learn(total_timesteps=time_steps)


