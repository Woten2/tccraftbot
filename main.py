import os
import discord
from discord.ext import commands
from discord import app_commands
import mcstatus
from flask import Flask
from threading import Thread
import datetime
import asyncio
import random
import aiohttp

# === TOKEN ===
BOT_TOKEN = os.environ.get('DISCORD_TOKEN')

if not BOT_TOKEN:
    print("❌ DISCORD_TOKEN bulunamadı!")
    exit(1)

# === FLASK WEB SUNUCU (Wake-up) ===
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

# === DISCORD BOT ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='tc!', intents=intents, help_command=None, case_insensitive=True)

# ============================================
# GİZLİ SUNUCU BİLGİLERİ
# ============================================
GIZLI_IP = "104.239.83.40"
SERVER_DOMAIN = "oyna.tccraft.com.tr"

SERVERS = {
    "Lobi": 25566,
    "Towny": 25567,
    "SMP": 25568,
    "SkyBlock": 25569,
    "BoxPVP": 25570,
    "TrapPVP": 25571
}

# ============================================
# ROL ID
# ============================================
ROL_ID = 1527706174424612934  # Sunucu Kesintileri Rolü

# ============================================
# OLAY (EVENT) - on_ready
# ============================================
@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    await bot.change_presence(activity=discord.Game(name="tc!yardım"))
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash komut senkronize edildi!")
    except Exception as e:
        print(f"❌ Slash komut senkronizasyon hatası: {e}")

# ============================================
# OLAY (EVENT) - on_message (Case Insensitive)
# ============================================
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

# ============================================
# MODAL - KOD GİRME KUTUSU (TÜM SUNUCULAR İÇİN)
# ============================================
class KodModal(discord.ui.Modal, title="🔗 Hesap Eşleştirme Kodu"):
    def __init__(self, sunucu_adi):
        super().__init__()
        self.sunucu_adi = sunucu_adi
        
        self.kod = discord.ui.TextInput(
            label=f"Minecraft {sunucu_adi} - Aldığın Kod",
            placeholder="Örnek: 123456",
            min_length=4,
            max_length=20,
            required=True
        )
        self.add_item(self.kod)
    
    async def on_submit(self, interaction: discord.Interaction):
        kod = self.kod.value
        sunucu = self.sunucu_adi
        
        await interaction.response.send_message(
            f"✅ **Kod alındı!**\n"
            f"Sunucu: `{sunucu}`\n"
            f"Kod: `{kod}`\n\n"
            f"⏳ Minecraft sunucusu ile doğrulanıyor...",
            ephemeral=True
        )
        
        # Burada RCON ile sunucuya komut gönder
        # Örnek: /skript run discord_esle("oyuncu", kod)

# ============================================
# SLASH KOMUT: /rolverme
# ============================================
@bot.tree.command(
    name="rolverme",
    description="Sunucu kesintilerinden haberdar olmak için rol al veya çıkar!"
)
@app_commands.default_permissions(administrator=True)
async def rolverme(interaction: discord.Interaction):
    role = interaction.guild.get_role(ROL_ID)
    
    if role is None:
        await interaction.response.send_message(
            "❌ **Rol bulunamadı!** Lütfen bot sahibine bildirin.",
            ephemeral=True
        )
        return
    
    al_button = discord.ui.Button(
        label="✅ Rol Al",
        style=discord.ButtonStyle.green,
        custom_id="rol_al"
    )
    
    cikar_button = discord.ui.Button(
        label="❌ Rolü Çıkar",
        style=discord.ButtonStyle.red,
        custom_id="rol_cikar"
    )
    
    view = discord.ui.View()
    view.add_item(al_button)
    view.add_item(cikar_button)
    
    embed = discord.Embed(
        title="🔔 Sunucu Kesintileri Bildirimleri",
        description="Sunucu kesintileri, bakım ve güncellemeler hakkında anında bilgi almak için aşağıdaki butonlardan birini seç!",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📌 Ne Kazanırsın?",
        value="• Anlık kesinti bildirimleri\n• Bakım duyuruları\n• Güncelleme haberleri\n• Özel etkinlik duyuruları",
        inline=False
    )
    embed.set_footer(text="TCCRAFT • Her zaman bilgilen!")
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

# ============================================
# SLASH KOMUT: /eslebutonboxpvp
# ============================================
@bot.tree.command(
    name="eslebutonboxpvp",
    description="BoxPVP sunucusu için hesap eşleştirme butonu oluştur!"
)
@app_commands.default_permissions(administrator=True)
async def eslebutonboxpvp(interaction: discord.Interaction):
    button = discord.ui.Button(
        label="🔗 BoxPVP - Hesabını Eşleştir",
        style=discord.ButtonStyle.primary,
        custom_id="esle_boxpvp"
    )
    view = discord.ui.View()
    view.add_item(button)
    
    embed = discord.Embed(
        title="🔗 BoxPVP Hesap Eşleştirme",
        description="**3 Günlük VIP Ödülü!** 🎉",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="📝 Nasıl Yapılır?",
        value="1️⃣ **Minecraft BoxPVP'de** `/discordesle` yaz ve kodu al\n"
              "2️⃣ Aşağıdaki butona tıkla\n"
              "3️⃣ Aldığın kodu kutuya yaz ve gönder\n"
              "4️⃣ **3 Günlük VIP** kazan! 🎁",
        inline=False
    )
    await interaction.response.send_message(embed=embed, view=view)

# ============================================
# SLASH KOMUT: /eslebutonsmp
# ============================================
@bot.tree.command(
    name="eslebutonsmp",
    description="SMP sunucusu için hesap eşleştirme butonu oluştur!"
)
@app_commands.default_permissions(administrator=True)
async def eslebutonsmp(interaction: discord.Interaction):
    button = discord.ui.Button(
        label="🔗 SMP - Hesabını Eşleştir",
        style=discord.ButtonStyle.primary,
        custom_id="esle_smp"
    )
    view = discord.ui.View()
    view.add_item(button)
    
    embed = discord.Embed(
        title="🔗 SMP Hesap Eşleştirme",
        description="**3 Günlük VIP Ödülü!** 🎉",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="📝 Nasıl Yapılır?",
        value="1️⃣ **Minecraft SMP'de** `/discordesle` yaz ve kodu al\n"
              "2️⃣ Aşağıdaki butona tıkla\n"
              "3️⃣ Aldığın kodu kutuya yaz ve gönder\n"
              "4️⃣ **3 Günlük VIP** kazan! 🎁",
        inline=False
    )
    await interaction.response.send_message(embed=embed, view=view)

# ============================================
# SLASH KOMUT: /eslebutontowny
# ============================================
@bot.tree.command(
    name="eslebutontowny",
    description="Towny sunucusu için hesap eşleştirme butonu oluştur!"
)
@app_commands.default_permissions(administrator=True)
async def eslebutontowny(interaction: discord.Interaction):
    button = discord.ui.Button(
        label="🔗 Towny - Hesabını Eşleştir",
        style=discord.ButtonStyle.primary,
        custom_id="esle_towny"
    )
    view = discord.ui.View()
    view.add_item(button)
    
    embed = discord.Embed(
        title="🔗 Towny Hesap Eşleştirme",
        description="**3 Günlük VIP Ödülü!** 🎉",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="📝 Nasıl Yapılır?",
        value="1️⃣ **Minecraft Towny'de** `/discordesle` yaz ve kodu al\n"
              "2️⃣ Aşağıdaki butona tıkla\n"
              "3️⃣ Aldığın kodu kutuya yaz ve gönder\n"
              "4️⃣ **3 Günlük VIP** kazan! 🎁",
        inline=False
    )
    await interaction.response.send_message(embed=embed, view=view)

# ============================================
# SLASH KOMUT: /eslebutontrappvp
# ============================================
@bot.tree.command(
    name="eslebutontrappvp",
    description="TrapPVP sunucusu için hesap eşleştirme butonu oluştur!"
)
@app_commands.default_permissions(administrator=True)
async def eslebutontrappvp(interaction: discord.Interaction):
    button = discord.ui.Button(
        label="🔗 TrapPVP - Hesabını Eşleştir",
        style=discord.ButtonStyle.primary,
        custom_id="esle_trappvp"
    )
    view = discord.ui.View()
    view.add_item(button)
    
    embed = discord.Embed(
        title="🔗 TrapPVP Hesap Eşleştirme",
        description="**3 Günlük VIP Ödülü!** 🎉",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="📝 Nasıl Yapılır?",
        value="1️⃣ **Minecraft TrapPVP'de** `/discordesle` yaz ve kodu al\n"
              "2️⃣ Aşağıdaki butona tıkla\n"
              "3️⃣ Aldığın kodu kutuya yaz ve gönder\n"
              "4️⃣ **3 Günlük VIP** kazan! 🎁",
        inline=False
    )
    await interaction.response.send_message(embed=embed, view=view)

# ============================================
# SLASH KOMUT: /eslebutonskyblock
# ============================================
@bot.tree.command(
    name="eslebutonskyblock",
    description="SkyBlock sunucusu için hesap eşleştirme butonu oluştur!"
)
@app_commands.default_permissions(administrator=True)
async def eslebutonskyblock(interaction: discord.Interaction):
    button = discord.ui.Button(
        label="🔗 SkyBlock - Hesabını Eşleştir",
        style=discord.ButtonStyle.primary,
        custom_id="esle_skyblock"
    )
    view = discord.ui.View()
    view.add_item(button)
    
    embed = discord.Embed(
        title="🔗 SkyBlock Hesap Eşleştirme",
        description="**3 Günlük VIP Ödülü!** 🎉",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="📝 Nasıl Yapılır?",
        value="1️⃣ **Minecraft SkyBlock'ta** `/discordesle` yaz ve kodu al\n"
              "2️⃣ Aşağıdaki butona tıkla\n"
              "3️⃣ Aldığın kodu kutuya yaz ve gönder\n"
              "4️⃣ **3 Günlük VIP** kazan! 🎁",
        inline=False
    )
    await interaction.response.send_message(embed=embed, view=view)

# ============================================
# BUTON ETKİLEŞİMLERİ
# ============================================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id")
        
        # --- /rolverme BUTONLARI ---
        if custom_id == "rol_al":
            role = interaction.guild.get_role(ROL_ID)
            if role is None:
                await interaction.response.send_message("❌ **Rol bulunamadı!**", ephemeral=True)
                return
            if role in interaction.user.roles:
                await interaction.response.send_message(f"❌ **Zaten `{role.name}` rolüne sahipsin!**", ephemeral=True)
                return
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"✅ **Başarıyla `{role.name}` rolü verildi!**", ephemeral=True)
            except:
                await interaction.response.send_message("❌ **Botun yetkisi yok!**", ephemeral=True)
            return
        
        elif custom_id == "rol_cikar":
            role = interaction.guild.get_role(ROL_ID)
            if role is None:
                await interaction.response.send_message("❌ **Rol bulunamadı!**", ephemeral=True)
                return
            if role not in interaction.user.roles:
                await interaction.response.send_message(f"❌ **Zaten `{role.name}` rolüne sahip değilsin!**", ephemeral=True)
                return
            try:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(f"✅ **Başarıyla `{role.name}` rolü çıkarıldı!**", ephemeral=True)
            except:
                await interaction.response.send_message("❌ **Botun yetkisi yok!**", ephemeral=True)
            return
        
        # --- /eslebuton BUTONLARI ---
        elif custom_id == "esle_boxpvp":
            await interaction.response.send_modal(KodModal("BoxPVP"))
        elif custom_id == "esle_smp":
            await interaction.response.send_modal(KodModal("SMP"))
        elif custom_id == "esle_towny":
            await interaction.response.send_modal(KodModal("Towny"))
        elif custom_id == "esle_trappvp":
            await interaction.response.send_modal(KodModal("TrapPVP"))
        elif custom_id == "esle_skyblock":
            await interaction.response.send_modal(KodModal("SkyBlock"))

# ============================================
# PREFIX KOMUT: tc!sunucu
# ============================================
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
            server = mcstatus.JavaServer(f"{GIZLI_IP}:{port}", timeout=5)
            status = server.status()
            
            online_count += 1
            total_players += status.players.online
            
            if status.players.online > 0:
                status_emoji = "🟢"
            else:
                status_emoji = "🟡"
            
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

# ============================================
# PREFIX KOMUT: tc!yardım
# ============================================
@bot.command(name='yardım')
async def yardim(ctx):
    embed = discord.Embed(
        title="📚 TCCRAFT Bot Komutları",
        description="Tüm komutlar **DM** olarak gönderilir!",
        color=discord.Color.blue()
    )
    embed.add_field(name="🎮 `tc!sunucu`", value=f"**{SERVER_DOMAIN}** üzerindeki tüm sunucuların durumunu gösterir.", inline=False)
    embed.add_field(name="👤 `tc!oyuncular`", value="Tüm sunuculardaki çevrimiçi oyuncuları listeler.", inline=False)
    embed.add_field(name="❓ `tc!yardım`", value="Bu komut listesini gösterir.", inline=False)
    embed.add_field(name="🌐 `tc!ping`", value="Botun gecikmesini gösterir.", inline=False)
    embed.add_field(name="📊 `tc!istatistik`", value="Bot istatistiklerini gösterir.", inline=False)
    embed.add_field(name="⏰ `tc!zaman`", value="Zaman dilimini gösterir.", inline=False)
    embed.add_field(name="🤖 `tc!botbilgi`", value="Bot hakkında detaylı bilgi verir.", inline=False)
    embed.add_field(name="📌 `/rolverme`", value="Sunucu kesintilerinden haberdar olmak için rol al veya çıkar! **(Sadece Yetkililer)**", inline=False)
    embed.add_field(name="📌 `/eslebutonboxpvp`", value="BoxPVP sunucusu için hesap eşleştirme butonu oluştur! **(Sadece Yetkililer)**", inline=False)
    embed.add_field(name="📌 `/eslebutonsmp`", value="SMP sunucusu için hesap eşleştirme butonu oluştur! **(Sadece Yetkililer)**", inline=False)
    embed.add_field(name="📌 `/eslebutontowny`", value="Towny sunucusu için hesap eşleştirme butonu oluştur! **(Sadece Yetkililer)**", inline=False)
    embed.add_field(name="📌 `/eslebutontrappvp`", value="TrapPVP sunucusu için hesap eşleştirme butonu oluştur! **(Sadece Yetkililer)**", inline=False)
    embed.add_field(name="📌 `/eslebutonskyblock`", value="SkyBlock sunucusu için hesap eşleştirme butonu oluştur! **(Sadece Yetkililer)**", inline=False)
    embed.set_footer(text="TCCRAFT • Her zaman oyunda! 🎯")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("📨 Yardım menüsü DM olarak gönderildi!", delete_after=5)

# ============================================
# PREFIX KOMUT: tc!oyuncular
# ============================================
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
            server = mcstatus.JavaServer(f"{GIZLI_IP}:{port}", timeout=5)
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

# ============================================
# PREFIX KOMUT: tc!ping
# ============================================
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

# ============================================
# PREFIX KOMUT: tc!istatistik
# ============================================
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

# ============================================
# PREFIX KOMUT: tc!zaman
# ============================================
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

# ============================================
# PREFIX KOMUT: tc!botbilgi
# ============================================
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

# ============================================
# BOTU BAŞLAT
# ============================================
keep_alive()
bot.run(BOT_TOKEN)