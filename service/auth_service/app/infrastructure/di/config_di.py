from app.config import Config
from dishka import Provider, Scope, provide


class ConfigProvider(Provider):
    scope = Scope.APP
    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    @provide
    def provide_config(self) -> Config:
        return self.config