
import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_ROLE_NAME = "Shop Admin"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

shop_enabled = True


def is_shop_admin(interaction):
    return (
        interaction.user.guild_permissions.administrator
        or any(role.name == ADMIN_ROLE_NAME
               for role in interaction.user.roles)
    )


class ListingModal(discord.ui.Modal, title="Phantom-Mart | New Listing"):
    product = discord.ui.TextInput(
        label="Product Name",
        placeholder="Example: Minecraft Rank",
        max_length=100
    )

    price = discord.ui.TextInput(
        label="Price",
        placeholder="Example: ₹199",
        max_length=50
    )

    stock = discord.ui.TextInput(
        label="Stock",
        placeholder="Example: 5 available",
        max_length=50
    )

    description = discord.ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not is_shop_admin(interaction):
            await interaction.response.send_message(
                "You are not authorised.",
                ephemeral=True
            )
            return

        if not shop_enabled:
            await interaction.response.send_message(
                "Shop listings are currently OFF.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Choose the channel for this listing:",
            view=ChannelSelectView(),
            ephemeral=True
        )


class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            channel_types=[discord.ChannelType.text],
            placeholder="Select shop channel",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction):
        if not is_shop_admin(interaction):
            await interaction.response.send_message(
                "Not authorised.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Please submit the listing details again using the panel.",
            ephemeral=True
        )


class ChannelSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(ChannelSelect())


class ShopPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Listing",
        style=discord.ButtonStyle.primary,
        emoji="🛒",
        custom_id="phantom:create"
    )
    async def create_listing(self, interaction, button):
        if not is_shop_admin(interaction):
            await interaction.response.send_message(
                "You are not authorised.",
                ephemeral=True
            )
            return

        if not shop_enabled:
            await interaction.response.send_message(
                "Shop is OFF.",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(ListingModal())

    @discord.ui.button(
        label="Toggle Shop",
        style=discord.ButtonStyle.danger,
        emoji="🔴",
        custom_id="phantom:toggle"
    )
    async def toggle_shop(self, interaction, button):
        global shop_enabled

        if not is_shop_admin(interaction):
            await interaction.response.send_message(
                "You are not authorised.",
                ephemeral=True
            )
            return

        shop_enabled = not shop_enabled

        await interaction.response.send_message(
            "🟢 Shop is ON" if shop_enabled else "🔴 Shop is OFF",
            ephemeral=True
        )


@bot.event
async def on_ready():
    bot.add_view(ShopPanel())
    print(f"Phantom-Mart online as {bot.user}")


@bot.command()
@commands.has_permissions(administrator=True)
async def panel(ctx):
    embed = discord.Embed(
        title="PHANTOM-MART",
        description="Official Shop Management Panel\n\n"
                    "Create and manage your product listings here.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Phantom-Mart | Shop System")

    await ctx.send(embed=embed, view=ShopPanel())


bot.run(TOKEN)
