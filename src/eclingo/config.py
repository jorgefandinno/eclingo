class AppConfig(object):
    """
    Class for application specific options.
    """

    def __init__(
        self, semantics="g94", verbose=0, eclingo_rewritten="no", rewritten_program=[]
    ):
        self.eclingo_verbose = verbose
        self.eclingo_semantics = semantics
        self.eclingo_rewritten = eclingo_rewritten
        self.rewritten_program = rewritten_program
