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

# === BOT ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='tc!', intents=intents, help_command=None, case_insensitive=True)

# ============================================
# ROL ID
# ============================================
ROL_ID = 1527706174424612934  # Sunucu Kesintileri Rolü

# ============================================
# SLASH KOMUT (ROL VER / ROL ÇIKAR - AYRI BUTONLAR)
# ============================================
@bot.tree.command(name="rolverme", description="Sunucu kesintilerinden haberdar olmak için rol al veya çıkar!")
async def rolverme(interaction: discord.Interaction):
    role = interaction.guild.get_role(ROL_ID)
    
    if role is None:
        await interaction.response.send_message(
            "❌ **Rol bulunamadı!** Lütfen bot sahibine bildirin.",
            ephemeral=True
        )
        return
    
    # İki buton oluştur
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
    
    # Kullanıcının mevcut durumu
    has_role = role in interaction.user.roles
    durum = f"✅ **{role.name}** rolüne sahipsin!" if has_role else f"❌ **{role.name}** rolüne sahip değilsin!"
    
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
    embed.add_field(
        name="📌 Mevcut Durumun",
        value=durum,
        inline=False
    )
    embed.set_footer(text="TCCRAFT • Her zaman bilgilen!")
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

# ============================================
# BUTON ETKİLEŞİMLERİ
# ============================================
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        role = interaction.guild.get_role(ROL_ID)
        
        if role is None:
            await interaction.response.send_message(
                "❌ **Rol bulunamadı!** Lütfen bot sahibine bildirin.",
                ephemeral=True
            )
            return
        
        # --- ROL AL BUTONU ---
        if interaction.data.get("custom_id") == "rol_al":
            if role in interaction.user.roles:
                await interaction.response.send_message(
                    f"❌ **Zaten `{role.name}` rolüne sahipsin!**",
                    ephemeral=True
                )
                return
            
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"✅ **Başarıyla `{role.name}` rolü verildi!**\nArtık sunucu kesintilerinden haberdar olacaksın.",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ **Botun yetkisi yok!** Botun rol verme yetkisi olduğundan emin ol.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ **Bir hata oluştu:** {e}",
                    ephemeral=True
                )
        
        # --- ROL ÇIKAR BUTONU ---
        elif interaction.data.get("custom_id") == "rol_cikar":
            if role not in interaction.user.roles:
                await interaction.response.send_message(
                    f"❌ **Zaten `{role.name}` rolüne sahip değilsin!**",
                    ephemeral=True
                )
                return
            
            try:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"✅ **Başarıyla `{role.name}` rolü çıkarıldı!**\nArtık bildirim almayacaksın.",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ **Botun yetkisi yok!** Botun rol çıkarma yetkisi olduğundan emin ol.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ **Bir hata oluştu:** {e}",
                    ephemeral=True
                )

# ============================================
# PREFIX KOMUTLAR
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

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yapıldı!')
    await bot.change_presence(activity=discord.Game(name="tc!yardım"))
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash komut senkronize edildi!")
    except Exception as e:
        print(f"❌ Slash komut senkronizasyon hatası: {e}")

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

# ---------- tc!yardım ----------
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
    embed.add_field(name="📌 `/rolverme`", value="Sunucu kesintilerinden haberdar olmak için rol al veya çıkar!", inline=False)
    embed.set_footer(text="TCCRAFT • Her zaman oyunda! 🎯")
    
    await ctx.author.send(embed=embed)
    if ctx.guild:
        await ctx.message.delete()
        await ctx.send("📨 Yardım menüsü DM olarak gönderildi!", delete_after=5)

# ---------- tc!oyuncular ----------
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
                value="*Sunucu kapalı veya ulaşılamıyor*",
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