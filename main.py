import gym
# import gym_minigrid
# from gym_minigrid.wrappers import *
from stable_baselines_master.stable_baselines import DQN
from action_filters import GrammarFilter, AllPassFilter


if __name__ == '__main__':
    time_steps = 5000
    # os.environ["PATH"] += os.pathsep + 'C:\\ffmpeg\\bin' uncomment if used in windows

    env = gym.make('CartPole-v1')

    def checkpoints(episode_id):
        episodes = [1000, 5000, 10000, 20000, 30000]
        return episode_id in episodes

    # env = gym.wrappers.Monitor(env, "./videos", video_callable=checkpoints, force=True)

    # env = gym.make('random_rooms-v0', max_steps=100, goal_visible_in_room=False, upsample=10)
    # env = gym.make('MiniGrid-Empty-16x16-v0')
    # env = ImgObsWrapper(env)
    # env = RandomRoomsEnv(rows=100, cols=100, max_steps=500, goal_visible_in_room=False, upsample=1)

    log_dir = "./log"

    # model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, filter=GrammarFilter(history_size=100), grammar_on_exploration=False)
    model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, full_tensorboard_log=False,
                filter=AllPassFilter(), NotOnExpo=False)
    # model = DQN('MlpPolicy', env, verbose=1, tensorboard_log=log_dir)

    model.learn(total_timesteps=time_steps, tb_log_name="test")
