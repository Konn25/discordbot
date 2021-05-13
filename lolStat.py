import discord
from discord.ext import commands

from riotwatcher import LolWatcher, ApiError

import requests
import json

with open("key.txt") as f:
    content = f.readlines()
content = [x.strip() for x in content] 

bot = commands.Bot(command_prefix="!")

lol_watcher = LolWatcher(content[1])
my_region = 'EUN1'

@bot.command()
async def summoner(ctx,arg):
    data=lol_watcher.summoner.by_name(my_region,arg)
    data2=lol_watcher.data_dragon.champions
    print(data2)

    embed=discord.Embed(title=data['name'],  description="A felhasználó szintje: ", color=discord.Color.blue())
    embed.set_thumbnail(url="https://icon-library.net/images/league-of-legends-icon/league-of-legends-icon-10.jpg")
    embed.add_field(name="Szint: ", value=str(data['summonerLevel']), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def champData(ctx,arg):
    request = get_jsonparsed_data("http://ddragon.leagueoflegends.com/cdn/11.9.1/data/hu_HU/champion.json")
    content=json.dumps(request)
    load=json.loads(content)
    champsname=request['data']
    data=""
    for ss in champsname:
        if(load['data'][str(ss)]['name']==str(arg)):
            embed=discord.Embed(title=load['data'][str(ss)]['name'], color=discord.Color.blue())
            data += "Rang: "+str(load['data'][str(ss)]['title'])+"\n"
            data += "Info: "+str(load['data'][str(ss)]['blurb'])+"\n"
            data += "HP: "+str(load['data'][str(ss)]['stats']['hp'])+"\n"
            data += "Páncél: "+str(load['data'][str(ss)]['stats']['armor'])+"\n"
            data += "Mozgási sebesség: "+str(load['data'][str(ss)]['stats']['movespeed'])+"\n"
            data += "Sebzés: "+str(load['data'][str(ss)]['stats']['attackdamage'])+"\n"
            embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/11.9.1/img/champion/"+str(load['data'][str(ss)]['name'])+".png")
            embed.add_field(name="Rövid ismertető: ",value=data, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def champName(ctx):
    request = get_jsonparsed_data("http://ddragon.leagueoflegends.com/cdn/11.9.1/data/hu_HU/champion.json")
    content=json.dumps(request)
    load=json.loads(content)
    champsname=request['data']
    names=""
    for ss in champsname:
        names +=str(load['data'][str(ss)]['name'])+"\n"

    
    embed=discord.Embed(title="Hősök", color=discord.Color.blue())

    embed.set_thumbnail(url="https://icon-library.net/images/league-of-legends-icon/league-of-legends-icon-10.jpg")
    embed.add_field(name="A hősök nevei: ",value="Hősök", inline=False)
    embed.set_footer(text=names)
    await ctx.send(embed=embed)




@bot.command()
async def currentFreeChamp(ctx,region):
    currnetlist =  lol_watcher._champion.rotations(region)

    champs=get_jsonparsed_data("http://ddragon.leagueoflegends.com/cdn/11.9.1/data/hu_HU/champion.json")
    campsname = len(champs['data'])
    print(campsname)
    print(len(currnetlist['freeChampionIds']))
    print(currnetlist['freeChampionIds'])
    freeChamp=currnetlist['freeChampionIds']
    
    semmi=[""]
    for ss in champs['data']:
        semmi.append(ss)

    valami=[]
    for kk in range(0,len(semmi)):
        valami.append(extract_element_from_json(champs['data'], [str(semmi[kk]),'key']))

    free=[]
    for tt in range(0,len(valami)):
        valami[tt]=str(valami[tt]).replace("[\'",'')
        valami[tt]=str(valami[tt]).replace('\']','')
        valami[tt]=str(valami[tt]).replace("[\"",'')
        valami[tt]=str(valami[tt]).replace('\"]','')
      
        for rr in range(0,(len(freeChamp))):
            if(str(freeChamp[rr])==str(valami[tt])):
                champion=str(extract_element_from_json(champs['data'], [str(semmi[tt]),'name']))
                free.append(str(champion))

    free=list(map(lambda st: str.replace(st, "[\'",''), free))
    free=list(map(lambda st: str.replace(st, '\']',''), free))
    free=list(map(lambda st: str.replace(st, '\"]',''), free))
    free=list(map(lambda st: str.replace(st, "[\"",''), free))

    embed=discord.Embed(title="Ingyenes hősök", color=discord.Color.blue())
    embed.set_thumbnail(url="https://icon-library.net/images/league-of-legends-icon/league-of-legends-icon-10.jpg")

    sor=""
    for ff in range(0,len(free)):
        sor +=str(free[ff])+"\n"
        
    embed.add_field(name="Név: ",value=sor, inline=False)
    await ctx.send(embed=embed)

def get_jsonparsed_data(url):
        r = requests.get(url)
        return r.json()


def extract_element_from_json(obj, path):
    def extract(obj, path, ind, arr):

        key = path[ind]
        if ind + 1 < len(path):
            if isinstance(obj, dict):
                if key in obj.keys():
                    extract(obj.get(key), path, ind + 1, arr)
                else:
                    arr.append(None)
            elif isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        extract(item, path, ind, arr)
            else:
                arr.append(None)
        if ind + 1 == len(path):
            if isinstance(obj, list):
                if not obj:
                    arr.append(None)
                else:
                    for item in obj:
                        arr.append(item.get(key, None))
            elif isinstance(obj, dict):
                arr.append(obj.get(key, None))
            else:
                arr.append(None)
        return arr
    if isinstance(obj, dict):
        return extract(obj, path, 0, [])
    elif isinstance(obj, list):
        outer_arr = []
        for item in obj:
            outer_arr.append(extract(item, path, 0, []))
        return outer_arr

bot.run(content[0])
