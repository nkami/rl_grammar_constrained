from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.deepq.policies import MlpPolicy
from stable_baselines import DQN
from gym_grammar.envs import FourRoomsEnv
from action_filters import AllPassFilter


if __name__ == '__main__':
    time_steps = 25000
    env = FourRoomsEnv()
    env = DummyVecEnv([lambda: env])
    log_dir = "./log/"

    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, filter=AllPassFilter())
    model.learn(total_timesteps=time_steps)


