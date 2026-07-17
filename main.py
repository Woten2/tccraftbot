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

# === SUNUCU BİLGİLERİ (GİZLİ) ===
SERVER_IP = "104.239.83.40"          # Sayısal IP (sorgulama buradan yapılır)
SERVER_DOMAIN = "oyna.tccraft.com.tr"  # Gösterilecek domain

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

# ---------- tc!sunucu ----------
@bot.command(name='sunucu')
async def sunucu_durumu(ctx):
    await ctx.typing()
    try:
        # Sayısal IP'den sorgula (gizli)
        server = mcstatus.JavaServer(SERVER_IP, timeout=5)
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
        # Domain göster (sayısal IP gizli)
        embed.add_field(name="📡 Sunucu", value=f"`{SERVER_DOMAIN}`", inline=False)
        embed.add_field(name="📌 Sürüm", value=f"`{status.version.name}`", inline=True)
        embed.add_field(name="👥 Oyuncu", value=f"**{status.players.online}** / {status.players.max}", inline=True)
        embed.add_field(name="🔄 Gecikme", value=f"`{status.latency*1000:.1f} ms`", inline=True)
        embed.add_field(name="📝 MOTD", value=f"```{status.motd}```", inline=False)
        embed.add_field(name="👤 Çevrimiçi Oyuncular", value=f"```{player_list}```", inline=False)
        embed.set_footer(text="TCCRAFT • tc!yardım ile tüm komutları gör")
        
        await ctx.author.send(embed=embed)
        if ctx.guild:
            await ctx.message.delete()
            await ctx.send("✅ Bilgiler DM olarak gönderildi!", delete_after=5)
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Hata!",
            description=f"Sunucuya ulaşılamıyor veya bir hata oluştu.\n```{str(e)}```",
            color=discord.Color.red()
        )
        await ctx.author.send(embed=error_embed)
        if ctx.guild:
            await ctx.message.delete()
            await ctx.send("❌ Hata oluştu, DM'ni kontrol et!", delete_after=5)

# ---------- tc!yardım ----------
@bot.command(name='yardım')
async def yardim(ctx):
    embed = discord.Embed(
        title="📚 TCCRAFT Bot Komutları",
        description="Tüm komutlar **DM** olarak gönderilir!",
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
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("📨 Yardım menüsü DM olarak gönderildi!", delete_after=5)

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

# ---------- tc!oyuncular ----------
@bot.command(name='oyuncular')
async def oyuncular(ctx):
    await ctx.typing()
    try:
        # Sayısal IP'den sorgula (gizli)
        server = mcstatus.JavaServer(SERVER_IP, timeout=5)
        query = server.query()
        players = query.players.names if query.players.names else ["Oyuncu yok"]
        
        if players == ["Oyuncu yok"]:
            await ctx.author.send("📭 **Sunucuda şu anda oyuncu yok!**")
        else:
            player_list = "\n".join([f"• {p}" for p in players])
            embed = discord.Embed(
                title=f"👥 Çevrimiçi Oyuncular ({len(players)})",
                description=player_list,
                color=discord.Color.green()
            )
            await ctx.author.send(embed=embed)
        
        if ctx.guild:
            await ctx.message.delete()
            await ctx.send("✅ Oyuncu listesi DM olarak gönderildi!", delete_after=5)
    except Exception as e:
        await ctx.author.send(f"❌ Hata: {e}")
        if ctx.guild:
            await ctx.message.delete()

# ---------- tc!trafik ----------
@bot.command(name='trafik')
async def trafik(ctx):
    try:
        # Sayısal IP'den sorgula (gizli)
        server = mcstatus.JavaServer(SERVER_IP, timeout=5)
        status = server.status()
        
        embed = discord.Embed(
            title="📈 Sunucu Trafik Bilgisi",
            color=discord.Color.blue()
        )
        embed.add_field(name="👥 Şu Anki Oyuncu", value=f"{status.players.online}/{status.players.max}", inline=True)
        embed.add_field(name="📊 Maksimum Oyuncu", value=status.players.max, inline=True)
        embed.add_field(name="📌 Sürüm", value=status.version.name, inline=True)
        embed.set_footer(text="TCCRAFT • Trafik bilgileri")
        
        await ctx.author.send(embed=embed)
        if ctx.guild:
            await ctx.message.delete()
            await ctx.send("✅ Trafik bilgileri DM olarak gönderildi!", delete_after=5)
    except Exception as e:
        await ctx.author.send(f"❌ Hata: {e}")
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
    embed.add_field(name="🔗 Bağlantı", value="[TCCRAFT](https://tccraft.com.tr)", inline=False)
    embed.set_footer(text="TCCRAFT • tc!yardım ile tüm komutları gör")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()

# === BAŞLAT ===
keep_alive()
bot.run(BOT_TOKEN)