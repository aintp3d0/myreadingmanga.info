from litestar import Litestar, Controller, get


class Index(Controller):
    path = "/"

    @get()
    async def handler(self) -> None: ...


class Manga(Controller):
    path = "/manga"

    @get()
    async def handler(self) -> None: ...


app = Litestar(route_handlers=[Index, Manga])
