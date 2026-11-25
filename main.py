import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp

# تحميل المتغيرات من ملف .env
load_dotenv()

# ============================================================
# ⚠️ هنا تضع التوكن والـ ID (عبر ملف .env وليس مباشرة هنا)
# ============================================================
DISCORD_TOKEN = os.getenv("9108879482:AAGkG6Tem7lnGAdIJbBw_vzwNT0gjbvXxM8")   # توكن البوت
MY_ID = int(os.getenv("MY_ID", "8308876698"))          # آيدي حسابك الشخصي
CLAUDE_API_KEY = os.getenv("")  # مفتاح Anthropic API
# ============================================================

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# موديل Claude
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

# تعليمات النظام - تخصص البوت في الأمن السيبراني
SYSTEM_PROMPT = """أنت مساعد خبير في الأمن السيبراني والاختبار الأخلاقي (Ethical Hacking).
مهامك:
- شرح تقنيات الاختراق الأخلاقي والدفاع.
- تحليل الثغرات (مثل OWASP Top 10).
- شرح أدوات مثل Nmap, Burp Suite, Metasploit, Wireshark.
- مساعدة في CTF و HackTheBox و TryHackMe.
- تقديم أوامر Linux وBash لفحص الأنظمة (فقط على أنظمة تملك صلاحية عليها).

قواعد صارمة:
1. لا تساعد في أي نشاط اختراق غير قانوني أو استهداف أنظمة بدون إذن.
2. ارفض أي طلب يهدف لإيذاء الآخرين.
3. ذكّر المستخدم دائماً بأهمية الإذن القانوني.
4. أجب بالعربية إذا كتب المستخدم بالعربية.

كن مختصراً وواضحاً، واستخدم تنسيق Discord (``` للكود)."""


@bot.event
async def on_ready():
    print(f"✅ تم تسجيل الدخول باسم: {bot.user}")
    print(f"🆔 ID البوت: {bot.user.id}")
    print(f"👤 صاحب البوت ID: {MY_ID}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="أمن سيبراني أخلاقي 🛡️ | !help"
        )
    )


async def ask_claude(prompt: str, history: list = None) -> str:
    """إرسال السؤال إلى Claude API وإرجاع الرد"""
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    messages = history or []
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1500,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(CLAUDE_API_URL, headers=headers, json=payload) as resp:
            if resp.status != 200:
                err = await resp.text()
                return f"❌ خطأ من Claude API: {resp.status}\n```{err[:300]}```"
            data = await resp.json()
            return data["content"][0]["text"]


@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🛡️ بوت الأمن السيبراني",
        description="مساعدك في Ethical Hacking بواسطة Claude AI",
        color=0x00ff88
    )
    embed.add_field(name="!ask <سؤال>", value="اسأل Claude عن أي موضوع أمني", inline=False)
    embed.add_field(name="!nmap <target>", value="شرح أوامر Nmap", inline=False)
    embed.add_field(name="!payload <نوع>", value="أمثلة Payloads تعليمية", inline=False)
    embed.add_field(name="!tools", value="قائمة الأدوات المهمة", inline=False)
    embed.add_field(name="!ctf", value="نصائح لحل تحديات CTF", inline=False)
    embed.set_footer(text="⚠️ للاستخدام التعليمي والأخلاقي فقط")
    await ctx.send(embed=embed)


@bot.command(name="ask")
async def ask_cmd(ctx, *, question: str = None):
    if not question:
        await ctx.send("❌ اكتب سؤالك بعد الأمر. مثال: `!ask ما هو SQL Injection؟`")
        return
    async with ctx.typing():
        answer = await ask_claude(question)
    # تقسيم الردود الطويلة
    for i in range(0, len(answer), 1900):
        await ctx.send(answer[i:i+1900])


@bot.command(name="nmap")
async def nmap_cmd(ctx, *, target: str = None):
    prompt = f"أعطني أوامر Nmap لفحص الهدف التالي بشكل تعليمي: {target or 'بدون هدف محدد'}. اشرح كل خيار."
    async with ctx.typing():
        answer = await ask_claude(prompt)
    await ctx.send(f"```\n{answer[:1900]}\n```" if len(answer) < 1900 else answer[:1900])


@bot.command(name="payload")
async def payload_cmd(ctx, *, ptype: str = None):
    prompt = f"اشرح payloads تعليمية من نوع {ptype or 'XSS'} وكيفية الحماية منها. للتعليم فقط."
    async with ctx.typing():
        answer = await ask_claude(prompt)
    await ctx.send(answer[:1900])


@bot.command(name="tools")
async def tools_cmd(ctx):
    embed = discord.Embed(title="🛠️ أدوات الاختراق الأخلاقي", color=0x00aaff)
    tools = {
        "فحص الشبكات": "Nmap, Netcat, Masscan",
        "تحليل الويب": "Burp Suite, OWASP ZAP",
        "استغلال": "Metasploit, SQLMap",
        "كلمات المرور": "Hashcat, John the Ripper",
        "التنصت": "Wireshark, tcpdump",
        "هندسة عكسية": "Ghidra, IDA Pro, radare2",
        "توزيعات": "Kali Linux, Parrot OS",
    }
    for k, v in tools.items():
        embed.add_field(name=k, value=v, inline=False)
    embed.set_footer(text="⚠️ استخدمها فقط على أنظمة تملك إذناً")
    await ctx.send(embed=embed)


@bot.command(name="ctf")
async def ctf_cmd(ctx):
    prompt = "أعطني 5 نصائح احترافية للنجاح في تحديات CTF (Capture The Flag)."
    async with ctx.typing():
        answer = await ask_claude(prompt)
    await ctx.send(answer[:1900])


# أمر خاص بصاحب البوت فقط
@bot.command(name="restart")
async def restart_cmd(ctx):
    if ctx.author.id != MY_ID:
        await ctx.send("❌ هذا الأمر لصاحب البوت فقط.")
        return
    await ctx.send("🔄 جاري إعادة التشغيل...")
    await bot.close()


# تشغيل البوت
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("❌ لم يتم العثور على DISCORD_TOKEN في ملف .env")
    bot.run(DISCORD_TOKEN)
