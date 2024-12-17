import discord, random, requests
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='$', intents=intents)

print(discord.__file__)  # Esto debería mostrar la ruta al módulo `discord.py` oficial

help = ["noticias", "categorias"]


API_KEY = "f3798e116eb342b2bae58e7f0cbd9c11"
CANTIDAD_NOTICIAS = 8

def fetch_noticias_from_api(categoria, cantidad=CANTIDAD_NOTICIAS):
    try:
        url = f"https://newsapi.org/v2/everything?q={categoria}&language=es&apiKey={API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        noticias = data.get("articles", [])[:cantidad]
        return [
            {
                "title": noticia.get("title"),
                "image": noticia.get("urlToImage", "../static/img/default_image.jpg"),
                "date": noticia.get("publishedAt", "").split("T")[0],
                "source": noticia.get("source", {}).get("name"),
                "url": noticia.get("url"),
            }
            for noticia in noticias
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener noticias: {e}")
        return []


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Bienvenido {member.mention} a {guild.name}!, Los comandos que hay los puedes revisar en $helper'
        await guild.system_channel.send(to_send)

@bot.command()
async def helper(ctx):

    to_send = (f'Estos son los comandos funcionales: {help}')
    await ctx.send(to_send)

@bot.command()
async def noticias(ctx, *, categoria=None):
    # Lista de categorías disponibles
    categorias_disponibles = ["tecnología", "salud", "negocios", "entretenimiento", "ciencia"]

    # Si no se especifica categoría, selecciona una aleatoria
    if not categoria:
        categoria = random.choice(categorias_disponibles)

    # Verifica que la categoría sea válida
    if categoria not in categorias_disponibles:
        await ctx.send(f"Categoría no válida. Las categorías disponibles son: {', '.join(categorias_disponibles)}.")
        return

    # Fetch noticias de la API para la categoría seleccionada
    noticias = fetch_noticias_from_api(categoria, cantidad=8)

    if noticias:  # Verifica que se obtuvieron noticias
        # Seleccionar una noticia aleatoria
        noticia = random.choice(noticias)

        # Crear el mensaje con el formato de la noticia
        mensaje = (
            f"Categoría: **{categoria.capitalize()}**\n"
            f"**{noticia['title']}**\n"
            f"{noticia['source']} - {noticia['date']}\n"
            f"[Leer más]({noticia['url']})"
        )
        # Enviar el mensaje al canal
        await ctx.send(mensaje)
    else:
        # Si no hay noticias disponibles
        await ctx.send(f"Lo siento, no pude obtener noticias de la categoría {categoria} en este momento.")

@bot.command()
async def categorias(ctx):
    categorias_dispo = ["tecnología", "salud", "negocios", "entretenimiento", "ciencia"]
    await ctx.send(f"Estas son las categorias disponibles: {categorias_dispo}")


bot.run('MTMxNzk0OTIzOTUzOTc5Mzk5MA.GsJ5KA.ya8y3gVMv2TEoPWfB0o0CrV0LhIsPYSm4rzR0s')