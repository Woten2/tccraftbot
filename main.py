import os
import discord
from discord.ext import commands
import mcstatus
from flask import Flask
from threading import Thread
import datetime

# === TOKEN ===
BOT_TOKEN = os.environ.get('DISCORD_TOKEN')

if not BOT_TOKEN:
    print("❌ DISCORD_TOKEN bulunamadı!")
    exit(1)

# === FLASK ===
app = Flask('')

@app.route('/')
def wake_up():
    return "Bot aktif! ✅"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# === BOT (CASE INSENSITIVE) ===
intents = discord.Intents.all()

class CustomBot(commands.Bot):
    async def get_prefix(self, message):
        prefixes = ['tc!', 'TC!', 'Tc!', 'tC!']
        for prefix in prefixes:
            if message.content.startswith(prefix):
                return prefix
        return 'tc!'

bot = CustomBot(
    command_prefix='tc!',
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# === GİZLİ SUNUCU BİLGİLERİ (Kodda, gözükmez) ===
BASE_IP = "104.239.83.40"          # Gizli - sadece kodda
SERVER_DOMAIN = "oyna.tccraft.com.tr"  # Gösterilecek domain

# Portlar gizli - sadece kodda (25566-25571)
SERVERS = {
    "Lobi": 25566,
    "Towny": 25567,
    "SMP": 25568,
    "SkyBlock": 25569,
    "BoxPVP": 25570,
    "TrapPVP": 25571
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    await bot.change_presence(activity=discord.Game(name="tc!yardım"))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    prefixes = ['tc!', 'TC!', 'Tc!', 'tC!']
    for prefix in prefixes:
        if message.content.startswith(prefix):
            await bot.process_commands(message)
            return
    await bot.process_commands(message)

# ---------- tc!sunucu (TÜM SUNUCULAR - PORTLAR GİZLİ) ----------
@bot.command(name='sunucu')
async def sunucu_durumu(ctx):
    await ctx.typing()
    
    embed = discord.Embed(
        title="🎮 TCCRAFT Sunucular",
        description=f"**{SERVER_DOMAIN}**",
        color=discord.Color.blue(),
        timestamp=ctx.message.created_at
    )
    
    online_count = 0
    total_players = 0
    
    for server_name, port in SERVERS.items():
        try:
            server = mcstatus.JavaServer(f"{BASE_IP}:{port}", timeout=3)
            status = server.status()
            
            online_count += 1
            total_players += status.players.online
            
            if status.players.online > 0:
                status_emoji = "🟢"
            else:
                status_emoji = "🟡"
            
            # Gösterimde port yok, sadece sunucu adı ve oyuncu bilgisi
            embed.add_field(
                name=f"{status_emoji} {server_name}",
                value=f"👥 `{status.players.online}` / {status.players.max}\n"
                      f"📌 `{status.version.name}`\n"
                      f"🔄 `{status.latency*1000:.0f}ms`",
                inline=True
            )
        except:
            embed.add_field(
                name=f"🔴 {server_name}",
                value="❌ **Kapalı**",
                inline=True
            )
    
    embed.set_footer(
        text=f"✅ {online_count}/{len(SERVERS)} aktif • {total_players} oyuncu • tc!yardım"
    )
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("✅ Sunucu bilgileri DM olarak gönderildi!", delete_after=5)

# ---------- tc!yardım (PORTLAR GÖSTERMEZ) ----------
@bot.command(name='yardım')
async def yardim(ctx):
    embed = discord.Embed(
        title="📚 TCCRAFT Bot Komutları",
        description="Tüm komutlar **DM** olarak gönderilir!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🎮 `tc!sunucu`",
        value=f"**{SERVER_DOMAIN}** üzerindeki tüm sunucuların durumunu gösterir.",
        inline=False
    )
    embed.add_field(
        name="👤 `tc!oyuncular`",
        value="Tüm sunuculardaki çevrimiçi oyuncuları listeler.",
        inline=False
    )
    embed.add_field(name="❓ `tc!yardım`", value="Bu komut listesini gösterir.", inline=False)
    embed.add_field(name="🌐 `tc!ping`", value="Botun gecikmesini gösterir.", inline=False)
    embed.add_field(name="📊 `tc!istatistik`", value="Bot istatistiklerini gösterir.", inline=False)
    embed.add_field(name="⏰ `tc!zaman`", value="Zaman dilimini gösterir.", inline=False)
    embed.add_field(name="🤖 `tc!botbilgi`", value="Bot hakkında detaylı bilgi verir.", inline=False)
    embed.set_footer(text="TCCRAFT • Her zaman oyunda! 🎯")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("📨 Yardım menüsü DM olarak gönderildi!", delete_after=5)

# ---------- tc!oyuncular (TÜM SUNUCULAR - PORT GÖSTERMEZ) ----------
@bot.command(name='oyuncular')
async def oyuncular(ctx):
    await ctx.typing()
    
    embed = discord.Embed(
        title="👥 Tüm Sunuculardaki Oyuncular",
        color=discord.Color.green(),
        timestamp=ctx.message.created_at
    )
    
    total_players = 0
    has_players = False
    
    for server_name, port in SERVERS.items():
        try:
            server = mcstatus.JavaServer(f"{BASE_IP}:{port}", timeout=3)
            query = server.query()
            players = query.players.names if query.players.names else []
            
            if players:
                has_players = True
                total_players += len(players)
                player_list = "\n".join([f"• {p}" for p in players[:15]])
                if len(players) > 15:
                    player_list += f"\n... ve {len(players)-15} oyuncu daha"
                embed.add_field(
                    name=f"🟢 {server_name} ({len(players)})",
                    value=player_list,
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"🟡 {server_name}",
                    value="*Oyuncu yok*",
                    inline=False
                )
        except:
            embed.add_field(
                name=f"🔴 {server_name}",
                value="*Kapalı*",
                inline=False
            )
    
    if not has_players:
        embed.description = "📭 **Hiçbir sunucuda oyuncu yok!**"
    
    embed.set_footer(text=f"Toplam {total_players} oyuncu çevrimiçi")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("✅ Oyuncu listesi DM olarak gönderildi!", delete_after=5)

# ---------- tc!ping ----------
@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Gecikme: **{latency} ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.yellow() if latency < 300 else discord.Color.red()
    )
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()

# ---------- tc!istatistik ----------
@bot.command(name='istatistik')
async def istatistik(ctx):
    embed = discord.Embed(
        title="📊 Bot İstatistikleri",
        color=discord.Color.purple()
    )
    embed.add_field(name="🤖 Bot Adı", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📚 Sunucu Sayısı", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Kullanıcı Sayısı", value=len(bot.users), inline=True)
    embed.add_field(name="⏰ Çalışma Süresi", value="Bot aktif ✅", inline=True)
    embed.add_field(name="🔗 Bağlantı", value=f"[{SERVER_DOMAIN}](https://{SERVER_DOMAIN})", inline=True)
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()

# ---------- tc!zaman ----------
@bot.command(name='zaman')
async def zaman(ctx):
    now = datetime.datetime.now()
    embed = discord.Embed(
        title="⏰ Zaman Bilgisi",
        color=discord.Color.blue()
    )
    embed.add_field(name="📅 Tarih", value=now.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🕐 Saat", value=now.strftime("%H:%M:%S"), inline=True)
    embed.add_field(name="🌍 Zaman Dilimi", value="UTC+3 (Türkiye)", inline=True)
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()

# ---------- tc!botbilgi ----------
@bot.command(name='botbilgi')
async def botbilgi(ctx):
    embed = discord.Embed(
        title="🤖 Bot Bilgileri",
        color=discord.Color.blue()
    )
    embed.add_field(name="📛 İsim", value=bot.user.name, inline=True)
    embed.add_field(name="🆔 ID", value=bot.user.id, inline=True)
    embed.add_field(name="📅 Oluşturulma", value=bot.user.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📚 Sunucu Sayısı", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Toplam Kullanıcı", value=len(bot.users), inline=True)
    embed.add_field(name="⚙️ Gecikme", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="📌 Prefix", value="`tc!` (büyük/küçük harf duyarsız)", inline=False)
    embed.add_field(name="🔗 Bağlantı", value=f"[{SERVER_DOMAIN}](https://{SERVER_DOMAIN})", inline=False)
    embed.set_footer(text="TCCRAFT • tc!yardım ile tüm komutları gör")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()

# === BAŞLAT ===
keep_alive()
bot.run(BOT_TOKEN)