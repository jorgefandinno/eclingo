class AppConfig(object):
    """
    Class for application specific options.
    """

    def __init__(self, semantics="g94", verbose=0, use_reification=False):
        self.eclingo_verbose = verbose
        self.eclingo_semantics = semantics
        self.eclingo_reification = use_reification
