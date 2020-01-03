from stable_baselines_master.stable_baselines.deepq.dqn import DQN
import gym
from action_filters import AllPassFilter


if __name__ == '__main__':
    time_steps = 100000
    env_name = "LunarLander-v2"
    env = gym.make(env_name)
    log_dir = "./log/"

    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, filter=AllPassFilter())
    model.learn(total_timesteps=time_steps, tb_log_name="LunarLander-v2 : Action Repetition using Grammar")


