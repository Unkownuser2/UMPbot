import discord
from discord.ext import commands, tasks
import feedparser
import re
import uuid

bot_token = 'No u'  

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
bot.motion_data = {}

feed_items = []

feeds = [ 
        'https://brightagebeyond.com/',
        'https://casperforum.org/',
        'https://ianwrightsite.wordpress.com/',
        'https://cibcom.org/',
        'https://www.xn--hrdin-gra.se/tag/cybernetics.html',
        'https://michael-hudson.com/category/articles/',
        'https://monthlyreview.org/',
        'https://thenextrecession.wordpress.com/',
        'http://marklambertz.de/category/cybernetics/',
        'https://sitewithaview.ovh/arquivo-do-blogue/',
        'https://socialistplanningbeyondcapitalism.org/',
        'https://thematchastraw.beehiiv.com/',
        'https://www.culturematters.org.uk/index.php',

         ]
def retrieve_motion_data(guild_id):
    return bot.motion_data.get(guild_id)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="For Reactionaries"))
    print(f'Logged in as {bot.user}!')
    check_feeds.start()

@tasks.loop(hours=1) 
async def check_feeds():
    global feedItems
    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if entry.link not in feedItems:
                feedItems.append(entry.link)
                channel = bot.get_channel(1180218003191762974)
                if channel:
                    await channel.send(f'New item in feed: {entry.title}\n{entry.link}')

async def checkFeeds():
    global feedItems
    for feedUrl in feeds:
        feed = feedparser.parse(feedUrl)
        for entry in feed.entries:
            if entry.link not in feedItems:
                feedItems.append(entry.link)
                channel = bot.get_channel('1180218003191762974')
                if channel:
                    await channel.send(f'New item in feed: {entry.title}\n{entry.link}')

@bot.event
async def on_message(message):
    await bot.process_commands(message)  
    channel_id = 1180218003191762974 
    if str(message.channel.id) == channel_id:
        await message.add_reaction('🔴')

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return  

    if str(reaction.emoji) == '⭐' and reaction.count == 3:  
        print(f"Debug: Reaction count is 2. Original author: {reaction.message.author.mention}")
        target_channel_id = '1180218473478115338'
        target_channel = bot.get_channel(int(target_channel_id))
        if target_channel:
            embed = discord.Embed(
                title=f"Hall of Fame!",
                description=f'{reaction.message.content}\n\n**Famous words by:** {reaction.message.author.mention}',
                color=0xFF0000 
            )
            await target_channel.send(embed=embed)
        else:
            print(f"Debug: Target channel with ID {target_channel_id} not found.")

    elif str(reaction.emoji) == '🍍' and reaction.count == 3:  
        print(f"Debug: Reaction count is 2. Original author: {reaction.message.author.mention}")
        target_channel_id = '1180218825585733723'
        target_channel = bot.get_channel(int(target_channel_id))
        if target_channel:
            embed = discord.Embed(
                title=f"Hall of Fame!",
                description=f'{reaction.message.content}\n\n**Work by:** {reaction.message.author.mention}',
                color=0xFF0000 
            )
            await target_channel.send(embed=embed)
        else:
            print(f"Debug: Target channel with ID {target_channel_id} not found.")
    elif str(reaction.emoji) == '🔴' and str(reaction.message.channel.id) == '1180218003191762974' and reaction.count - 1 == 3:
        print(f"Debug: Reaction count is 3. Original author: {reaction.message.author.mention}")
        target_channel_id = '1180217967292723230'
        target_channel = bot.get_channel(int(target_channel_id))
        if target_channel:
            embed = discord.Embed(
                title=f"Breaking News!",
                description=f'{reaction.message.content}\n\n**News Shared by** {reaction.message.author.mention}',
                color=0xFF0000 
            )
            await target_channel.send(embed=embed)
        else:
            print(f"Debug: Target channel with ID {target_channel_id} not found.")

@bot.event
async def on_member_join(member):
    channel_id = 1180214054762061875
    channel = bot.get_channel(channel_id)

    if channel:
        await channel.send(f'**Welcome to the United Marxist Pact!** {member.mention}, Go read <#1180213434034438215> and verify at <#1180214360816242718>')
    else:
        print(f"Channel with ID {channel_id} not found.")

@bot.event
async def on_member_remove(member):
    channel_id = 1180214054762061875
    channel = bot.get_channel(channel_id)

    if channel:
        await channel.send(f'**Goodbye** {member.mention}, hope you come back soon!')
    else:
        print(f"Channel with ID {channel_id} not found.")

allowed_vote_role_name = "Mediator"
allowed_motion_role_name = "Mediator"
required_majority_percentage = 50


def validate_motion_tag(tag):

    pattern = re.compile(r'#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}')

    return bool(pattern.match(tag))

@bot.command()
async def propose_motion(ctx, *, motion):
    if discord.utils.get(ctx.author.roles, name=allowed_motion_role_name) is None:
        await ctx.send("You do not have the required role to propose a motion.")
        return

    motion_tag = str(uuid.uuid4())

    motion_data = {
        'motion': motion,
        'tag': motion_tag,  
        'votes': {'aye': 0, 'nay': 0, 'abstain': 0},
        'voters': []
    }
    bot.motion_data[ctx.guild.id] = motion_data
    await display_motion(ctx, required_majority=required_majority_percentage)

@bot.command()
async def kill_motion(ctx, motion_tag):

    motion_data = retrieve_motion_data(ctx.guild.id)

    print(f"Motion data: {motion_data}")
    print(f"Motion tag to kill: {motion_tag}")

    if motion_data and 'tag' in motion_data and motion_data['tag'] == motion_tag:

        bot.motion_data.pop(ctx.guild.id)
        await ctx.send(f"Motion with tag {motion_tag} has been terminated.")
    else:
        await ctx.send(f"No active motion found with the tag {motion_tag}.")

@bot.command()
async def aye(ctx, reason=None):
    await vote(ctx, 'aye', reason, required_majority=required_majority_percentage)

@bot.command()
async def nay(ctx, reason=None):
    await vote(ctx, 'nay', reason, required_majority=required_majority_percentage)

async def vote(ctx, decision, reason=None, required_majority=None):
    vote_role = discord.utils.get(ctx.guild.roles, name=allowed_vote_role_name)
    if vote_role is None or vote_role not in ctx.author.roles:
        await ctx.send("You do not have the required role to vote.")
        return
    motion_data = bot.motion_data.get(ctx.guild.id)

    if motion_data:
        if ctx.author.id not in motion_data['voters']:
            motion_data['votes'][decision] += 1
            motion_data['voters'].append(ctx.author.id)
            await display_motion(ctx, required_majority=required_majority)

            total_votes = sum(motion_data['votes'].values())

            if motion_data['votes']['aye'] >= required_majority:
                await ctx.send("Motion passed. :white_check_mark:")
            elif motion_data['votes']['nay'] + motion_data['votes']['abstain'] >= required_majority:
                await ctx.send("Motion failed. :x:")

            if total_votes >= required_majority:
                bot.motion_data.pop(ctx.guild.id)
    else:
        await ctx.send("No active motion found.")

async def display_motion(ctx, required_majority):

    motion_data = retrieve_motion_data(ctx.guild.id)

    if motion_data:

        total_votes = sum(motion_data['votes'].values())

        if total_votes > 0:
            required_majority_votes = int(total_votes * required_majority / 100)
            aye_votes = motion_data['votes'].get('aye', 0)
            nay_votes = motion_data['votes'].get('nay', 0)
            passed = aye_votes >= required_majority_votes and nay_votes < (total_votes - required_majority_votes)
        else:
            required_majority_votes = 0  
            passed = False

        embed = discord.Embed(title="Currently active motion", description=f"Motion: {motion_data['motion']}", color=0x00ff00)
        embed.add_field(name="Motion Tag", value=f"{motion_data['tag']}", inline=False)
        embed.add_field(name="For", value=f"{motion_data['votes']['aye']} :thumbsup:", inline=True)
        embed.add_field(name="Against", value=f"{motion_data['votes']['nay']} :thumbsdown:", inline=True)
        embed.add_field(name="Abstain", value=f"{motion_data['votes']['abstain']} :flag_white:", inline=True)
        embed.add_field(name="Vote Majority", value=f"With {required_majority}% majority, the motion will pass if {required_majority_votes} or more members vote.", inline=False)

        message = await ctx.send(embed=embed)

        reactions_added = [reaction.emoji for reaction in message.reactions]
        if '✅' not in reactions_added and passed ==True and total_votes > 0:
            await message.add_reaction('✅') 
            embed = discord.Embed(title="Motion Results", description=f"Motion: {motion_data['motion']}", color=0x00ff00)
            embed.add_field(name='Results',value=f"Motion for **{motion_data['motion']}** is passed")
            embed.set_footer(text=f"Motion tag - {motion_data['tag']}")
            await ctx.send("<@&1180212745761738894>")
            await ctx.send(embed=embed)
        elif '❌' not in reactions_added and  passed ==False and total_votes > 0:
            await message.add_reaction('❌')  
            embed = discord.Embed(title="Motion Results", description=f"Motion: {motion_data['motion']}", color=0x00ff00)
            embed.add_field(name='Results',value=f"Motion for **{motion_data['motion']}** has failed")
            embed.set_footer(text=f"Motion tag - {motion_data['tag']}")
            await ctx.send("<@&1180212745761738894>")
            await ctx.send(embed=embed)
    else:
        await ctx.send("No active motion found.")

@bot.command()
async def umplink(ctx):
    await ctx.reply("https://discord.gg/WWrEbYhB8r")

@bot.command()
async def commands(ctx):
    await ctx.reply("# Commands\n*.umplink* - **It shows you the link for the server**")

@bot.command()
async def marx(ctx):
    name = "Karl Marx"
    photo = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Karl_Marx_001.jpg/330px-Karl_Marx_001.jpg"

    embed = discord.Embed(
        title="1800s Socialists",
        description="Socialist Political leaders during the 1800s",
        colour=discord.Colour.red())
    embed.set_thumbnail(url=f"{photo}")
    embed.set_author(name=f'{name}', url="https://www.marxists.org/glossary/people/m/a.htm#marx",)
    embed.add_field(
        name="A brief biography",
        value=(
            "**Karl Marx (1818-1883)** was a German philosopher, economist, and political theorist known for his revolutionary ideas. "
            "Marx emphasized the existence and struggle between classes in society. "
            "In a letter to Weydemeyer in 1852, he outlined that classes are linked to specific historical phases of production and "
            "that class struggle inevitably leads to the dictatorship of the proletariat, marking a transitional phase toward a classless society."
        ),
        inline=False
    )
    embed.add_field(
        name="Notable Works",
        value=(
            "[The Communist Manifesto](https://www.marxists.org/archive/marx/works/1848/communist-manifesto/)\n"
            "[Das Kapital](https://www.marxists.org/archive/marx/works/1867-c1/)\n"
            "[The German Ideology](https://www.marxists.org/archive/marx/works/1845/german-ideology/)"
        ),
        inline=False
    )
    embed.set_footer(text="Sourced from Marxists Internet Archive")
    await ctx.send(embed=embed)

@bot.command()
async def lenin(ctx):
    name = "Vladimir Ilyich Lenin"
    photo = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Lenin_in_1920_%28cropped%29.jpg/674px-Lenin_in_1920_%28cropped%29.jpg"

    embed = discord.Embed(
        title="1900s Socialists",
        description="Socialist Political leaders during the 1900s",
        colour=discord.Colour.red())
    embed.set_thumbnail(url=f"{photo}")
    embed.set_author(name=f'{name}', url="https://www.marxists.org/glossary/people/l/e.htm#lenin",)
    embed.add_field(
        name="A brief biography",
        value=(
            "Vladimir Ilyich Lenin (1870-1924) was a key leader of the Bolshevik party, playing a crucial role in the October 1917 Revolution that brought the Workers to power in Russia. "
            "Lenin became the head of the Soviet government and served until 1922 when he retired due to ill health.  "
        ),
        inline=False
    )
    embed.add_field(
        name="Notable Works",
        value=(
            "[The State & Revolution](https://www.marxists.org/archive/lenin/works/1917/staterev/)\n"
            "[Imperialism, the Highest Stage of Capitalism](https://www.marxists.org/archive/lenin/works/1916/imp-hsc/)\n"
            "[Left Communism, an Infantile Disorder](https://www.marxists.org/archive/lenin/works/1920/lwc/index.htm)"
        ),
        inline=False
    )
    embed.set_footer(text="Sourced from Marxists Internet Archive")
    await ctx.send(embed=embed)

@bot.command()
async def engels(ctx):
    name = "Friedrich Engels"
    photo = "https://upload.wikimedia.org/wikipedia/commons/2/21/Friedrich_Engels_portrait_%28cropped%29.jpg"

    embed = discord.Embed(
        title="1800s Socialists",
        description="Socialist Political leaders during the 1800s",
        colour=discord.Colour.red())
    embed.set_thumbnail(url=f"{photo}")
    embed.set_author(name=f'{name}', url="https://www.marxists.org/archive/marx/engels-bicentennial/index.htm",)
    embed.add_field(
        name="A brief biography",
        value=(
            "Friedrich Engels (1820-1895), a vital figure in the Marxist movement and collaborator of Karl Marx, was born into a prosperous industrialist family in Prussia. "
            "Influenced by his experiences in Manchester, England, Engels developed a commitment to addressing the struggles of the working class.  "
            'His groundbreaking work, "The Condition of the Working Class in England," published in 1845, provided a detailed analysis of working-class conditions.  '
            "Friedrich Engels passed away on August 5, 1895, leaving a lasting legacy as a key architect of Marxism."
            "His commitment to understanding material conditions and advocating for the emancipation of the working class remains influential in revolutionary socialist thought."
        ),
        inline=False
    )
    embed.add_field(
        name="Notable Works",
        value=(
            "[The Communist Manifesto](https://www.marxists.org/archive/marx/works/1848/communist-manifesto/)\n"
            "[Socialism: Utopian & Scientific](https://www.marxists.org/archive/marx/works/1880/soc-utop/index.htm)\n"
            "[Principles of Communism](https://www.marxists.org/archive/marx/works/1847/11/prin-com.htm)"
        ),
        inline=False
    )
    embed.set_footer(text="Sourced from Marxists Internet Archive")
    await ctx.send(embed=embed)

@bot.command(name='purge')
async def purge(ctx, amount: int):
    if ctx.message.author.guild_permissions.manage_messages:
        try:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"{amount} messages deleted.", delete_after=5)
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages.")
    else:
        await ctx.send("You don't have the required permissions to use this command.")

bot.run(bot_token)