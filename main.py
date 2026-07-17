import os
import discord
from discord.ext import commands
import mcstatus
from flask import Flask
from threading import Thread

# === TOKEN'ı ENVIRONMENT VARIABLE'DAN AL ===
BOT_TOKEN = os.environ.get('DISCORD_TOKEN')

if not BOT_TOKEN:
    print("❌ DISCORD_TOKEN environment variable'ı bulunamadı!")
    print("📌 Render'a DISCORD_TOKEN eklemeyi unutma!")
    exit(1)

# === FLASK WEB SUNUCU ===
app = Flask('')

@app.route('/')
def wake_up():
    return "Bot aktif ve çalışıyor! ✅"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# === DISCORD BOT (Case Insensitive) ===
intents = discord.Intents.all()

# commands.Bot'e case_insensitive=True ekledim!
bot = commands.Bot(
    command_prefix='tc!',
    intents=intents,
    help_command=None,
    case_insensitive=True  # <--- BÜYÜK/KÜÇÜK HARF DUYARSIZ
)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    await bot.change_presence(activity=discord.Game(name="tc!yardım"))

# ---------- tc!sunucu ----------
@bot.command(name='sunucu')
async def sunucu_durumu(ctx):
    await ctx.typing()
    try:
        server = mcstatus.JavaServer("oyna.tccraft.com.tr", timeout=5)
        status = server.status()
        query = server.query()
        
        players = query.players.names if query.players.names else ["Oyuncu yok"]
        player_list = "\n".join(players[:20])
        if len(players) > 20:
            player_list += f"\n... ve {len(players)-20} oyuncu daha"
        
        embed = discord.Embed(
            title="🎮 TCCRAFT Sunucu Durumu",
            color=discord.Color.green() if status.players.online > 0 else discord.Color.red(),
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="📡 IP", value="`oyna.tccraft.com.tr`", inline=False)
        embed.add_field(name="📌 Sürüm", value=f"`{status.version.name}`", inline=True)
        embed.add_field(name="👥 Oyuncu", value=f"**{status.players.online}** / {status.players.max}", inline=True)
        embed.add_field(name="🔄 Gecikme", value=f"`{status.latency*1000:.1f} ms`", inline=True)
        embed.add_field(name="📝 MOTD", value=f"```{status.motd}```", inline=False)
        embed.add_field(name="👤 Çevrimiçi Oyuncular", value=f"```{player_list}```", inline=False)
        embed.set_footer(text="TCCRAFT • tc!yardım ile tüm komutları gör")
        
        await ctx.author.send(embed=embed)
        if ctx.guild:
            await ctx.message.delete()
            await ctx.send("✅ Bilgiler özel mesaj olarak gönderildi!", delete_after=5)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Hata!",
            description=f"Sunucuya ulaşılamıyor veya bir hata oluştu.\n```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.author.send(embed=error_embed)
        if ctx.guild:
            await ctx.message.delete()
            await ctx.send("❌ Hata oluştu, özel mesajını kontrol et!", delete_after=5)

# ---------- tc!yardım ----------
@bot.command(name='yardım')
async def yardim(ctx):
    embed = discord.Embed(
        title="📚 TCCRAFT Bot Komutları",
        description="Tüm komutlar **özel mesaj** olarak gönderilir!",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎮 `tc!sunucu`", value="Sunucu durumunu gösterir.", inline=False)
    embed.add_field(name="❓ `tc!yardım`", value="Bu komut listesini gösterir.", inline=False)
    embed.add_field(name="🌐 `tc!ping`", value="Botun gecikmesini gösterir.", inline=False)
    embed.add_field(name="📊 `tc!istatistik`", value="Bot istatistiklerini gösterir.", inline=False)
    embed.set_footer(text="TCCRAFT • Her zaman oyunda! 🎯")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("📨 Yardım menüsü özel mesaj olarak gönderildi!", delete_after=5)

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
    embed.add_field(name="🔗 Bağlantı", value="[TCCRAFT](https://tccraft.com.tr)", inline=True)
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()

# === BAŞLAT ===
keep_alive()
bot.run(BOT_TOKEN)