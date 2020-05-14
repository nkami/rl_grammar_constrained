import gym
import gym_minigrid
import os
from gym_minigrid.wrappers import *
import tensorflow as tf

#from stable_baselines_master.stable_baselines import DQN
#from stable_baselines_master.stable_baselines.bench import Monitor
#from stable_baselines_master.stable_baselines.deepq.policies import FeedForwardPolicy
#from stable_baselines_master.stable_baselines.a2c.utils import conv, linear, conv_to_fc, lstm

from stable_baselines.a2c.utils import conv, linear, conv_to_fc, lstm
from stable_baselines.deepq.policies import FeedForwardPolicy
from stable_baselines import DQN
from stable_baselines.bench import Monitor

from action_filters import GrammarFilter, AllPassFilter


def custom_cnn(scaled_images, **kwargs):
    """
    CNN from Nature paper.
    :param scaled_images: (TensorFlow Tensor) Image input placeholder
    :param kwargs: (dict) Extra keywords parameters for the convolutional layers of the CNN
    :return: (TensorFlow Tensor) The CNN output layer
    """
    activ = tf.nn.relu
    layer_1 = activ(conv(scaled_images, 'c1', n_filters=128, filter_size=8, stride=2, init_scale=np.sqrt(2), **kwargs))
    layer_2 = activ(conv(layer_1, 'c2', n_filters=64, filter_size=4, stride=2, init_scale=np.sqrt(2), **kwargs))
    layer_3 = activ(conv(layer_2, 'c3', n_filters=64, filter_size=3, stride=1, init_scale=np.sqrt(2), **kwargs))
    layer_3 = conv_to_fc(layer_3)
    return activ(linear(layer_3, 'fc1', n_hidden=512, init_scale=np.sqrt(2)))


# Custom Mlp/Cnn policy
class CustomDQNPolicy(FeedForwardPolicy):
    def __init__(self, *args, **kwargs):
        super(CustomDQNPolicy, self).__init__(*args, **kwargs, layer_norm=False, feature_extraction="cnn", cnn_extractor=custom_cnn)
        #super(CustomDQNPolicy, self).__init__(*args, **kwargs, layers=[4096, 4096, 4096], layer_norm=False, feature_extraction="mlp")


if __name__ == '__main__':
    time_steps = 600000

    # env = gym.make('random_rooms-v0', max_steps=100, goal_visible_in_room=False, upsample=10)
    env = gym.make('MiniGrid-MultiRoom-N2-S4-v0')
    env = ImgObsWrapper(FullyObsWrapper(ReseedWrapper(env, seeds=list(range(15)))))
    #def checkpoints(episode_id):
    #    episodes = [1, 200, 500, 1000, 5000, 10000, 20000, 30000, 100000, 300000, 500000]
    #    return episode_id in episodes
    #env = gym.wrappers.Monitor(env, "./videos/Grammar/NotOnExploration/1/", video_callable=checkpoints, force=True)
    #env = gym.wrappers.Monitor(env, "./videos/SB/3/", video_callable=checkpoints, force=True)

    log_dir = "./log4/"


    #model = DQN('CnnPolicy', env, verbose=1, tensorboard_log=log_dir, filter=GrammarFilter(history_size=40, negate_grammar=False), grammar_on_exploration=True)  
    model = DQN(CustomDQNPolicy, env, verbose=1, tensorboard_log=log_dir)


    #model.learn(total_timesteps=time_steps, tb_log_name="Minigrid_MultiN2_seed48_tile2_Cnn_GrammarHistory40_io_OnExploration")
    model.learn(total_timesteps=time_steps, tb_log_name="Minigrid_MultiN2_seed15_Cnn_128stride2x64x64x512")

