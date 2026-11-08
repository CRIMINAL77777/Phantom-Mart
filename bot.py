# Phantom-Mart update
import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_ROLE_NAME = "Shop Admin"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

shop_enabled = True


def is_admin(interaction):
    return (
        interaction.user.guild_permissions.administrator
        or any(role.name == ADMIN_ROLE_NAME
               for role in interaction.user.roles)
    )


class ListingModal(discord.ui.Modal, title="Phantom-Mart Listing"):
    def __init__(self):
        super().__init__()

        self.product = discord.ui.TextInput(
            label="Product Name",
            placeholder="Minecraft Rank",
            max_length=100
        )

        self.price = discord.ui.TextInput(
            label="Price",
            placeholder="₹199",
            max_length=50
        )

        self.stock = discord.ui.TextInput(
            label="Stock",
            placeholder="5 available",
            max_length=50
        )

        self.description = discord.ui.TextInput(
            label="Description",
            style=discord.TextStyle.paragraph,
            max_length=500
        )

        self.add_item(self.product)
        self.add_item(self.price)
        self.add_item(self.stock)
        self.add_item(self.description)

    async def on_submit(self, interaction):
        if not is_admin(interaction):
            await interaction.response.send_message(
                "Not authorised.", ephemeral=True
            )
            return

        if not shop_enabled:
            await interaction.response.send_message(
                "Shop is currently OFF.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Choose where to publish this listing:",
            view=PublishView(
                self.product.value,
                self.price.value,
                self.stock.value,
                self.description.value
            ),
            ephemeral=True
        )


class PublishView(discord.ui.View):
    def __init__(self, product, price, stock, description):
        super().__init__(timeout=300)
        self.product = product
        self.price = price
        self.stock = stock
        self.description = description

        self.add_item(ChannelPicker(self))

    
    async def publish(self, interaction, channel):
        if not is_admin(interaction):
            await interaction.response.send_message(
                "Not authorised.", ephemeral=True
            )
            return

        if not shop_enabled:
            await interaction.response.send_message(
                "Shop is OFF.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🛒 {self.product}",
            description=self.description,
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Price", value=self.price, inline=True)
        embed.add_field(name="📦 Stock", value=self.stock, inline=True)
        embed.set_footer(text="PHANTOM-MART | OFFICIAL SHOP")

        try:
            await channel.send(embed=embed)
            await interaction.response.send_message(
                f"✅ Published in {channel.mention}!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Missing permission to send messages or embeds in that channel.",
                ephemeral=True
            )
        except Exception as error:
            print(f"Publishing error: {error}")
            await interaction.response.send_message(
                f"❌ Publishing failed: {type(error).__name__}",
                ephemeral=True
            )

class ChannelPicker(discord.ui.ChannelSelect):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(
            channel_types=[discord.ChannelType.text],
            placeholder="Select a shop channel",
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction):
        channel = self.values[0]
        await self.parent.publish(interaction, channel)


class ShopPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Listing",
        style=discord.ButtonStyle.primary,
        emoji="🛒",
        custom_id="phantom:create"
    )
    async def create(self, interaction, button):
        if not is_admin(interaction):
            await interaction.response.send_message(
                "Not authorised.", ephemeral=True
            )
            return

        if not shop_enabled:
            await interaction.response.send_message(
                "Shop is OFF.", ephemeral=True
            )
            return

        await interaction.response.send_modal(ListingModal())

    @discord.ui.button(
        label="Toggle Shop",
        style=discord.ButtonStyle.danger,
        emoji="🔴",
        custom_id="phantom:toggle"
    )
    async def toggle(self, interaction, button):
        global shop_enabled

        if not is_admin(interaction):
            await interaction.response.send_message(
                "Not authorised.", ephemeral=True
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
        title="🔴 PHANTOM-MART",
        description="Official Shop Listing Panel\n\n"
                    "Create and publish your products easily.",
        color=discord.Color.blue()
    )

    embed.set_footer(text="PHANTOM-MART | SHOP MANAGEMENT")

    await ctx.send(embed=embed, view=ShopPanel())


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing!")

bot.run(TOKEN)

