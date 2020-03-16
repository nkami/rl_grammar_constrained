from cyk_prefix_parser import cyk_prefix_parser
from cyk_prefix_parser import cyk_original_parser
from cyk_prefix_parser import cfg2cnf

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
    def __call__(self, num_actions):
        # print('filtered', num_actions)
        # print(len(self.past_actions))
        return [True for _ in range(0, num_actions)]


class GrammarFilter(ActionFilter):

    
    def __init__(self, history_size=2, negate_grammar=False):
        super().__init__()
        cfg2cnf.converter("grammar.txt")
        if negate_grammar:
            self.cyk = cyk_original_parser.Grammar("grammar_cnf.txt")
        else:
            self.cyk = cyk_prefix_parser.Grammar("grammar_cnf.txt")
        self.MAX_HISTORY = history_size
        self.negate_grammar = negate_grammar

    def __call__(self, num_actions):
        """
        :param args: an action
        :param kwargs:
        :return: returns a bool: True if the action is legal, else False.
        """
        legal_actions = []
        for action in range(0, num_actions):
            string = ' '.join(self.past_actions) + " " + str(action)
            if self.negate_grammar:
                legal_actions.append((not self.cyk.parse(string)))
            else:
                legal_actions.append(self.cyk.parse(string))
        # avoiding all false actions
        for action in legal_actions:
            if action:
                return legal_actions
        return [True for action in range(0, num_actions)]

    def add_action(self, action):
        self.past_actions.append(str(action))
        if len(self.past_actions) >= self.MAX_HISTORY:
            self.reset_past()
