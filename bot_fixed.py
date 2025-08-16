import os
import discord
from threading import Thread
from flask import Flask
import datetime

# Pinga o bot para rodar no render
bot_start_time = datetime.datetime.now()
    
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está correr no render"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_flask).start()

TOKEN = "MTQwNTk0NTEwOTA2NDg0NzUxMA.GONGq3.fjTq_8MRvQF8pF8emzyi7ftNWW4tjH3FboaGOo"
LOG_CHANNEL_ID = 1405758758025695232

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

bot = discord.Bot(intents=intents)

def get_log_channel(guild_id=None):
    """Get log channel for a specific guild, or use default if none specified."""
    return bot.get_channel(LOG_CHANNEL_ID)

async def send_embed(embed, guild=None):
    """Send embed to appropriate log channel based on guild."""
    channel = get_log_channel(guild.id if guild else None)
    if channel:
        await channel.send(embed=embed)

@bot.slash_command(name='setlogchannel', description='Define o canal de logs para este servidor.')
async def setlogchannel(ctx, channel: discord.TextChannel):
    """Define o canal de logs para este servidor."""
    embed = discord.Embed(
        title="📋 Canal de Logs Definido",
        description=f"Canal de logs definido para {channel.mention}",
        color=0x00ff00
    )
    embed.add_field(name="Canal", value=channel.mention, inline=False)
    embed.add_field(name="Servidor", value=ctx.guild.name, inline=False)
    embed.set_footer(text=f"Comando executado por {ctx.author}")
    await ctx.respond(embed=embed)

@bot.event
async def on_ready():
    print(f"✅Logged in as {bot.user}")
    embed = discord.Embed(title="Bot Online", description=f"{bot.user} agora está online .", color=0x00ff00)
    await send_embed(embed)

@bot.slash_command(name='status', description='Mostra o status do bot.')
async def status(ctx):
    """Mostra o status do bot."""
    uptime = datetime.datetime.now() - bot_start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=0x00ff00
    )
    embed.add_field(name="Status", value="✅ online e a funcionar ", inline=False)
    embed.add_field(name="Uptime", value=f"{days}d {hours}h {minutes}m {seconds}s", inline=False)
    embed.add_field(name="Started", value=bot_start_time.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
    embed.add_field(name="Commands Available", value="/start, /help, /status, /setlogchannel", inline=False)
    embed.set_footer(text=f"Bot: {bot.user} | {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name='start', description='Inicia o bot e mostra informações básicas.')
async def start(ctx):
    """Comando inicial com informações do bot."""
    embed = discord.Embed(
        title="🚀 Bot Iniciado",
        description=f"Bem-vindo! Eu sou o {bot.user.name}",
        color=0x00ff00
    )
    embed.add_field(name="📋 Funções", value="• Monitoramento de mensagens\n• Log de eventos do servidor\n• Sistema de notificações", inline=False)
    embed.add_field(name="🔧 Comandos", value="• `/status` - Ver status do bot\n• `/help` - Ver ajuda e comandos\n• `/start` - Este comando\n• `/setlogchannel` - Definir canal de logs", inline=False)
    embed.add_field(name="📊 Status", value="✅ Online e funcionando", inline=False)
    embed.set_footer(text=f"Comando executado por {ctx.author} | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    await ctx.respond(embed=embed)

@bot.slash_command(name='help', description='Mostra todos os comandos disponíveis.')
async def help(ctx):
    """Mostra ajuda e lista de comandos."""
    embed = discord.Embed(
        title="📖 Ajuda - Comandos Disponíveis",
        description="Aqui estão todos os comandos do bot:",
        color=0x0099ff
    )
    
    embed.add_field(
        name="🤖 Comandos Principais",
        value=(
            "`/start` - Inicia o bot e mostra informações\n"
            "`/status` - Mostra status e uptime do bot\n"
            "`/help` - Mostra esta mensagem de ajuda\n"
            "`/setlogchannel` - Definir canal de logs"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📋 Eventos Monitorados",
        value=(
            "• Mensagens editadas/deletadas\n"
            "• Entrada/saída de membros\n"
            "• Atribuição de cargos\n"
            "• Criação de convites\n"
            "• Banimentos e kicks"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🔧 Configuração",
        value="O bot envia logs automaticamente no canal configurado",
        inline=False
    )
    
    embed.set_footer(text=f"Comando executado por {ctx.author} | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    await ctx.respond(embed=embed)


@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return
    embed=discord.Embed(
        title="📝 Mensagem Editada",
        color=0xf1c40f
    )
    embed.set_author(name=str(before.author),icon_url=before.author.avatar.url if before.author.avatar else None)
    embed.add_field(name="Canal",value=f"{before.channel.mention} (`{before.channel.id}`)",inline=False)
    embed.add_field(name="Antiga Mensagem", value=before.content or "(empty)", inline=False)
    embed.add_field(name="Nova Mensagem", value=after.content or "(empty)", inline=False)
    embed.add_field(
        name="Data da Mensagem",
        value=f"{before.created_at.strftime('%Y-%m-%d %H:%M:%S')} (há {(discord.utils.utcnow() - before.created_at).seconds // 3600} horas )",
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
    await send_embed(embed, before.guild)

@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    embed = discord.Embed(
        title="🏀 Mensagem Excluida",
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
    await send_embed(embed, message.guild)

@bot.event
async def on_member_join(member):
    embed=discord.Embed(
        description=f"{member} ({member.id}) Entrou no servidor.",
        color=0x2ecc71
    )
    embed.set_author(name=str(member), icon_url=member.avatar.url if member.avatar else None)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    created_at = member.created_at.strftime("%B-%d,%Y %I:%M:%p")
    embed.add_field(
        name="Criação da conta",
        value=f"{created_at} (há {(discord.utils.utcnow() - member.created_at).days// 365} anos )",
        inline=False
    )
    await send_embed(embed, member.guild)

@bot.event
async def on_member_update(before, after):
    added_roles = [role for role in after.roles if role not in before.roles]
    if added_roles:
        embed = discord.Embed(color=0x2ecc71)
        embed.set_author(name=str(after), icon_url=after.avatar.url if after.avatar else None)
        roles_str = " ".join([role.mention for role in added_roles])

        # Busca quem deu o cargo usando audit logs
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
        await send_embed(embed, after.guild)

@bot.event
async def on_invite_create(invite):
    embed = discord.Embed(
        description=f"{invite.inviter.mention} criou um convite*{invite.code}** em {invite.channel.mention}",
        color=0x7289da
    )
    embed.set_author(name=str(invite.inviter), icon_url=invite.inviter.avatar.url if invite.inviter.avatar else None)
    # Expiração
    expires_in = "Nunca expira" if invite.max_age == 0 else f"em {invite.max_age // 86400} dias"
    embed.add_field(name="Expiração", value=expires_in, inline=False)
    # IDs
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
    await send_embed(embed, invite.guild)
    
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
    embed.add_field(name="Razão", value=reason or "No reason provided", inline=False)
    embed.set_footer(text=f"{bot.user} • {discord.utils.utcnow().strftime('%m/%d/%Y %I:%M %p')}")
    await send_embed(embed, guild)

@bot.event
async def on_member_remove(member):
    # Ver de o membro foi kickcado
    guild = member.guild
    async for entry in guild.audit_logs(action=discord.AuditLogAction.kick, limit=1):
        if entry.target.id == member.id:
            embed = discord.Embed(title="Membro Kickado", color=0x1abc9c)
            embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
            embed.add_field(name="Por", value=f"{entry.user} ({entry.user.id})", inline=False)
            embed.add_field(name="Razão", value=entry.reason or "No reason provided", inline=False)
            await send_embed(embed, guild)
            return
    # se nao foi kickcado , saiu normalmente
    embed = discord.Embed(title="Membro saiu", description=f"{member} ({member.id}) Saiu do Servidor.", color=0xe67e22)
    await send_embed(embed, member.guild)

bot.run(TOKEN)
