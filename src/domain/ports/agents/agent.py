# class Agent(ABC):
#
#     def __init__(
#             self,
#             name,
#             max_retries: int=2,
#             verbose: bool=True,
#             logger: Any = None
#     ):
#         self.name = name
#         self.max_retries = max_retries
#         self.verbose = verbose
#         self.logger = logger
#
#     @abstractmethod
#     def execute(self, *args, **kwargs):
#         pass