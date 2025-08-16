import os
import discord
from discord.ext import commands
from threading import Thread
from flask import Flask
import datetime
import json

# ================= Flask para manter vivo no Render ==================
bot_start_time = datetime.datetime.now()
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está correr no render"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_flask).start()

# ================= Configuração do Bot ==================
# Carrega as configurações do bot

with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

TOKEN = config['bot']['token']
PREFIX = config['bot']['prefix']
DEFAULT_LOG_CHANNEL = int(config['bot']['default_log_channel'])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ================= Multi-Server JSON Storage ==================
GUILD_CONFIG_FILE = "guild_configs.json"

def load_guild_configs():
    """Load guild configurations from JSON file"""
    try:
        with open(GUILD_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_guild_configs(data):
    """Save guild configurations to JSON file"""
    with open(GUILD_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# carrega as configurações dos servidores
guild_configs = load_guild_configs()

def get_guild_config(guild_id):
    """Get configuration for a specific guild"""
    guild_id_str = str(guild_id)
    if guild_id_str not in guild_configs:
        guild_configs[guild_id_str] = {
            "log_channel": None,
            "welcome_channel": None
        }
        save_guild_configs(guild_configs)
    return guild_configs[guild_id_str]

def set_guild_log_channel(guild_id, channel_id):
    """Set log channel for a specific guild"""
    guild_config = get_guild_config(guild_id)
    guild_config['log_channel'] = channel_id
    save_guild_configs(guild_configs)

def get_log_channel(guild_id):
    """Get log channel for a specific guild"""
    guild_config = get_guild_config(guild_id)
    channel_id = guild_config.get('log_channel')
    
    if channel_id:
        return bot.get_channel(channel_id)
    
    # voltar para o canal padrão se não houver configuração específica
    return bot.get_channel(DEFAULT_LOG_CHANNEL)

async def send_embed(guild, embed):
    """Send embed to the log channel for a specific guild"""
    if not guild:
        print("❌ No guild provided for logging")
        return False
        
    channel = get_log_channel(guild.id)
    if channel:
        try:
            await channel.send(embed=embed)
            return True
        except discord.Forbidden:
            print(f"❌ Bot doesn't have permission to send messages in {channel.name}")
        except discord.HTTPException as e:
            print(f"❌ Failed to send embed: {e}")
    else:
        print(f"❌ No log channel configured for guild {guild.name}")
    return False

# ================= Eventos ==================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

    # Quando o bot ficar online, notifica se já houver canal de logs
    for guild in bot.guilds:
        embed = discord.Embed(
            title="🤖 Bot Online",
            description=f"{bot.user} agora está online.",
            color=0x00ff00
        )
        await send_embed(guild, embed)

@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return
    
    embed = discord.Embed(
        title="📝 Mensagem Editada",
        color=0xf1c40f
    )
    embed.set_author(name=str(before.author), icon_url=before.author.avatar.url if before.author.avatar else None)
    embed.add_field(name="Canal", value=f"{before.channel.mention} (`{before.channel.id}`)", inline=False)
    embed.add_field(name="Antiga Mensagem", value=before.content or "(empty)", inline=False)
    embed.add_field(name="Nova Mensagem", value=after.content or "(empty)", inline=False)
    embed.add_field(
        name="Data da Mensagem",
        value=f"{before.created_at.strftime('%Y-%m-%d %H:%M:%S')} (há {(discord.utils.utcnow() - before.created_at).seconds // 3600} horas)",
        inline=False
    )
    embed.add_field(
        name="IDs",
        value=(
            f"Mensagem(`{before.id}`)\n"
            f"Canal(`{before.channel.id}`)\n"
            f"{before.author.mention}(`{before.author.id}`)"
        ),
        inline=False
    )
    await send_embed(before.guild, embed)

@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    
    embed = discord.Embed(
        title="🏀 Mensagem Deletada",
        color=0xe74c3c
    )
    embed.set_author(name=str(message.author), icon_url=message.author.avatar.url if message.author.avatar else None)
    embed.add_field(name="Mensagem", value=message.content or "(empty)", inline=False)
    embed.add_field(
        name="Data da Mensagem",
        value=f"{message.created_at.strftime('%B %d, %Y %I:%M %p')} (há {(discord.utils.utcnow() - message.created_at).days} dias)",
        inline=False
    )
    embed.add_field(
        name="IDs",
        value=(
            f"Mensagem (`{message.id}`)\n"
            f"{message.channel.mention} (`{message.channel.id}`)\n"
            f"{message.author.mention} (`{message.author.id}`)"
        ),
        inline=False
    )
    embed.set_footer(text=f"{bot.user} • {discord.utils.utcnow().strftime('%m/%d/%Y %I:%M %p')}")
    await send_embed(message.guild, embed)

@bot.event
async def on_member_join(member):
    embed = discord.Embed(
        description=f"{member} ({member.id}) Entrou no servidor.",
        color=0x2ecc71
    )
    embed.set_author(name=str(member), icon_url=member.avatar.url if member.avatar else None)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    created_at = member.created_at.strftime("%B-%d,%Y %I:%M:%p")
    embed.add_field(
        name="Criação da conta",
        value=f"{created_at} (há {(discord.utils.utcnow() - member.created_at).days// 365} anos)",
        inline=False
    )
    await send_embed(member.guild, embed)

@bot.event
async def on_member_remove(member):
    guild = member.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
        if entry.target.id == member.id:
            embed = discord.Embed(title="Membro Kickado", color=0x1abc9c)
            embed.add_field(name="User", value=f"{member}", inline=False)
            embed.add_field(name="Por", value=f"{entry.user}", inline=False)
            embed.add_field(name="Razão", value=entry.reason or "Sem razão", inline=False)
            await send_embed(guild, embed)
            return
    
    embed = discord.Embed(title="Membro Saiu", description=f"{member} saiu do servidor.", color=0xe67e22)
    await send_embed(guild, embed)

@bot.event
async def on_member_ban(guild, user):
    reason = None
    try:
        ban_entry = await guild.fetch_ban(user)
        reason = ban_entry.reason
    except Exception:
        reason = None
    
    embed = discord.Embed(title="Membro Banido", color=0x8e44ad)
    embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
    embed.add_field(name="Guild", value=f"{guild.name} ({guild.id})", inline=False)
    embed.add_field(name="Reason", value=reason or "No reason provided", inline=False)
    embed.set_footer(text=f"{bot.user} • {discord.utils.utcnow().strftime('%m/%d/%Y %I:%M %p')}")
    await send_embed(guild, embed)

@bot.event
async def on_invite_create(invite):
    embed = discord.Embed(
        description=f"{invite.inviter.mention} criou a convite **{invite.code}** em {invite.channel.mention}",
        color=0x7289da
    )
    embed.set_author(name=str(invite.inviter), icon_url=invite.inviter.avatar.url if invite.inviter.avatar else None)
    expires_in = "Nunca expira" if invite.max_age == 0 else f"em {invite.max_age // 86400} dias"
    embed.add_field(name="Expiração", value=expires_in, inline=False)
    embed.add_field(
        name="IDs",
        value=(
            f"**{invite.code}**\n"
            f"{invite.inviter.mention} (`{invite.inviter.id}`)\n"
            f"{invite.channel.mention} (`{invite.channel.id}`)"
        ),
        inline=False
    )
    embed.set_footer(text=f"{bot.user} • {discord.utils.utcnow().strftime('%m/%d/%Y %I:%M %p')}")
    await send_embed(invite.guild, embed)

@bot.event
async def on_member_update(before, after):
    added_roles = [role for role in after.roles if role not in before.roles]
    if added_roles:
        embed = discord.Embed(color=0x2ecc71)
        embed.set_author(name=str(after), icon_url=after.avatar.url if after.avatar else None)
        roles_str = " ".join([role.mention for role in added_roles])

        executor = None
        reason = "Cargo atribuído"
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=5):
            if entry.target.id == after.id and any(role in entry.changes.after.roles for role in added_roles):
                executor = entry.user
                if executor.bot:
                    reason = "Autorole do bot"
                else:
                    reason = f"Cargo dado por {executor.mention}"
                break

        embed.add_field(name="Cargo(s) Dado(s)", value=f"+ {roles_str}", inline=False)
        embed.add_field(name="Razão", value=reason, inline=False)
        ids_value = f"{after.mention} (`{after.id}`)"
        if executor:
            ids_value += f"\n{executor.mention} (`{executor.id}`)"
        embed.add_field(name="IDs", value=ids_value, inline=False)
        embed.set_footer(text=f"{bot.user} • {discord.utils.utcnow().strftime('%m/%d/%Y %I:%M %p')}")
        await send_embed(after.guild, embed)

# ================= Slash Commands ==================
@bot.tree.command(name="status", description="Mostra o status do bot")
async def status(interaction: discord.Interaction):
    uptime = datetime.datetime.now() - bot_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    embed = discord.Embed(
        title="🤖 Bot Status",
        color=0x00ff00
    )
    embed.add_field(name="Status", value="✅ Online and running", inline=False)
    embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m {seconds}s", inline=False)
    embed.add_field(name="Started", value=bot_start_time.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
    embed.add_field(name="Commands", value="/status, /help, /setlogchannel", inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Mostra a lista de comandos disponíveis")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Lista de Comandos",
        description="Aqui estão os comandos disponíveis:",
        color=0x3498db
    )
    embed.add_field(name="/status", value="Mostra o status e uptime do bot.", inline=False)
    embed.add_field(name="/help", value="Mostra esta mensagem de ajuda.", inline=False)
    embed.add_field(name="/setlogchannel", value="Define o canal de logs para este servidor.", inline=False)
    embed.set_footer(text=f"Bot: {bot.user}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setlogchannel", description="Define o canal onde os logs serão enviados")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setlogchannel(interaction: discord.Interaction, canal: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    set_guild_log_channel(guild_id, canal.id)

    await interaction.response.send_message(f"✅ Canal de logs definido para {canal.mention}", ephemeral=True)

# ================= Run ==================
bot.run(TOKEN)
