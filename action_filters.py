from cyk_prefix_parser.CYK_Paser import Grammar


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


class GrammarFilter(ActionFilter):

    MAX_HISTORY = 2

    def __init__(self):
        super().__init__()
        self.cyk_prefix = Grammar("grammar.txt")

    def __call__(self, *args, **kwargs):
        """
        :param args: an action
        :param kwargs:
        :return: returns a bool: True if the action is legal, else False.
        """
        string = ' '.join(self.past_actions) + " " + str(args[0])
        return self.cyk_prefix.parse(string)

    def add_action(self, action):
        self.past_actions.append(str(action))
        if len(self.past_actions) >= self.MAX_HISTORY:
            self.reset_past()
