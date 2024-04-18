from discord import Interaction, Embed, Color

class EmbedData:
    title: str = None
    desc: str  = None
    color: hex = None
    image_url: str = None
    thumbnail_url: str = None
    footer: tuple[str, str] = None
    fields: list[tuple[str, str]] = []

    def embed(self) -> Embed:
        e = Embed()

        if (self.title):
            e.title = self.title

        if self.desc:
            e.description = self.desc

        if self.color:
            e.color = self.color

        if self.image_url:
            e.set_image(url=self.image_url)

        if self.thumbnail_url:
            e.set_thumbnail(url=self.thumbnail_url)

        if self.footer:
            e.set_footer(text=self.footer[0], icon_url=self.footer[1])

        for field in self.fields:
            e.add_field(name=field[0], value=field[1])

        return e

class ResponseWrapper:
    def __init__(self, ctx: Interaction, title: str, desc: str, color: Color = Color.yellow()) -> None:
        self.ctx: Interaction = ctx

        self.embed_data = EmbedData()
        self.embed_data.title = title
        self.embed_data.desc = desc
        self.embed_data.color = color
        self.embed_data.footer = (f"Used by: {ctx.user.name}", ctx.user.avatar.url)

    async def start(self):
        embed = self.embed_data.embed()
        await self.ctx.response.send_message(embed=embed)

    async def color(self, color: str):
            self.embed_data.color = color
            await self.ctx.edit_original_response(embed=self.embed_data.embed())

    async def desc(self, desc: str):
        self.embed_data.desc = desc
        e = self.embed_data.embed()
        await self.ctx.edit_original_response(embed=self.embed_data.embed())

    async def title(self, title: str):
        self.embed_data.title = title
        await self.ctx.edit_original_response(embed=self.embed_data.embed())

    async def photo(self, url: str):
        self.embed_data.image_url = url
        await self.ctx.edit_original_response(embed=self.embed_data.embed())

    async def thumbnail(self, url: str):
        self.embed_data.thumbnail_url = url
        await self.ctx.edit_original_response(embed=self.embed_data.embed())

    async def field(self, title: str, content: str):
        self.embed_data.fields = [(title, content)]
        await self.ctx.edit_original_response(embed=self.embed_data.embed())
