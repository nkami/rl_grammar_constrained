from gym.envs.registration import register

register(
    id='random_rooms-v0',
    entry_point='gym_random_rooms.envs:RandomRoomsEnv',
    reward_threshold=1,
)