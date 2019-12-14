from gym.envs.registration import register

register(
    id='four_rooms-v0',
    entry_point='gym_grammar.envs:FourRoomsEnv',
)