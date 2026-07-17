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

# === BOT (CASE INSENSITIVE - KESİN ÇÖZÜM) ===
intents = discord.Intents.all()

# 1. YÖNTEM: Bot oluştururken case_insensitive=True
bot = commands.Bot(
    command_prefix='tc!',
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# 2. YÖNTEM: Ekstra olarak on_message ile prefix kontrolü (YEDEK)
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Prefix kontrolü (büyük/küçük harf duyarsız)
    prefix = 'tc!'
    content = message.content.lower()
    
    if content.startswith(prefix):
        # Komutu işle
        await bot.process_commands(message)
    else:
        # Diğer mesajları işleme
        await bot.process_commands(message)

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
        embed.add_field(name="📡 Sunucu", value="`oyna.tccraft.com.tr`", inline=False)
        embed.add_field(name="📌 Sürüm", value=f"`{status.version.name}`", inline=True)
        embed.add_field(name="👥 Oyuncu", value=f"**{status.players.online}** / {status.players.max}", inline=True)
        embed.add_field(name="🔄 Gecikme", value=f"`{status.latency*1000:.1f} ms`", inline=True)
        embed.add_field(name="📝 MOTD", value=f"```{status.motd}```", inline=False)
        embed.add_field(name="👤 Çevrimiçi Oyuncular", value=f"```{player_list}```", inline=False)
        embed.set_footer(text="TCCRAFT • tc!yardım ile tüm komutları gör")
        
        await ctx.send(embed=embed, ephemeral=True)
        await ctx.message.delete()
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}", ephemeral=True)
        await ctx.message.delete()

# ---------- tc!yardım ----------
@bot.command(name='yardım')
async def yardim(ctx):
    embed = discord.Embed(
        title="📚 TCCRAFT Bot Komutları",
        description="Tüm komutlar **ephemeral (geçici)** olarak gönderilir!",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎮 `tc!sunucu`", value="Sunucu durumunu gösterir.", inline=False)
    embed.add_field(name="❓ `tc!yardım`", value="Bu komut listesini gösterir.", inline=False)
    embed.add_field(name="🌐 `tc!ping`", value="Botun gecikmesini gösterir.", inline=False)
    embed.add_field(name="📊 `tc!istatistik`", value="Bot istatistiklerini gösterir.", inline=False)
    embed.add_field(name="👤 `tc!oyuncular`", value="Çevrimiçi oyuncuları listeler.", inline=False)
    embed.add_field(name="📈 `tc!trafik`", value="Sunucu trafiğini gösterir.", inline=False)
    embed.add_field(name="⏰ `tc!zaman`", value="Zaman dilimini gösterir.", inline=False)
    embed.add_field(name="🤖 `tc!botbilgi`", value="Bot hakkında detaylı bilgi verir.", inline=False)
    embed.set_footer(text="TCCRAFT • Her zaman oyunda! 🎯")
    
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.message.delete()

# ---------- tc!ping ----------
@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Gecikme: **{latency} ms**",
        color=discord.Color.green() if latency < 100 else discord.Color.yellow() if latency < 300 else discord.Color.red()
    )
    await ctx.send(embed=embed, ephemeral=True)
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
    
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.message.delete()

# ---------- tc!oyuncular ----------
@bot.command(name='oyuncular')
async def oyuncular(ctx):
    await ctx.typing()
    try:
        server = mcstatus.JavaServer("oyna.tccraft.com.tr", timeout=5)
        query = server.query()
        players = query.players.names if query.players.names else ["Oyuncu yok"]
        
        if players == ["Oyuncu yok"]:
            await ctx.send("📭 **Sunucuda şu anda oyuncu yok!**", ephemeral=True)
        else:
            player_list = "\n".join([f"• {p}" for p in players])
            embed = discord.Embed(
                title=f"👥 Çevrimiçi Oyuncular ({len(players)})",
                description=player_list,
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, ephemeral=True)
        
        await ctx.message.delete()
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}", ephemeral=True)
        await ctx.message.delete()

# ---------- tc!trafik ----------
@bot.command(name='trafik')
async def trafik(ctx):
    try:
        server = mcstatus.JavaServer("oyna.tccraft.com.tr", timeout=5)
        status = server.status()
        
        embed = discord.Embed(
            title="📈 Sunucu Trafik Bilgisi",
            color=discord.Color.blue()
        )
        embed.add_field(name="👥 Şu Anki Oyuncu", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="📊 Maksimum Oyuncu", value=status.players.max, inline=True)
        embed.add_field(name="📌 Sürüm", value=status.version.name, inline=True)
        embed.set_footer(text="TCCRAFT • Trafik bilgileri")
        
        await ctx.send(embed=embed, ephemeral=True)
        await ctx.message.delete()
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}", ephemeral=True)
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
    
    await ctx.send(embed=embed, ephemeral=True)
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
    embed.add_field(name="🔗 Bağlantı", value="[TCCRAFT](https://tccraft.com.tr)", inline=False)
    embed.set_footer(text="TCCRAFT • tc!yardım ile tüm komutları gör")
    
    await ctx.send(embed=embed, ephemeral=True)
    await ctx.message.delete()

# === BAŞLAT ===
keep_alive()
bot.run(BOT_TOKEN)