cyk_parser = __import__("cyk-prefix-parser.CYK_Paser")


class ActionFilter:
    """
    An object that determines which actions are legal.
    """
    def __init__(self):
        self.past_actions = []

    def __call__(self, *args, **kwargs):
        """
        :param args: an action
        :param kwargs:
        :return: returns a bool: True if the action is legal, else False.
        """
        pass

    def add_action(self, action):
        self.past_actions.append(action)

    def reset_past(self):
        self.past_actions = []


class AllPassFilter(ActionFilter):
    """
    All actions are always legal.
    """
    def __call__(self, *args, **kwargs):
        return True


