import requests
from pyrogram import filters
from YukkiMusic import app


@app.on_message(filters.command(["FAKE", "fake"]))
async def fkadress(_, message):
    query = message.text.split(maxsplit=1)[1].strip()  # Kullanıcının girdiği ülke adını al
    url = f"https://randomuser.me/api/?nat={query}"  # API URL'sini oluştur
    response = requests.get(url)  # API'den veri al
    data = response.json()  # JSON formatında veriyi al

    if "results" in data:  # Eğer sonuç varsa
        fk = data["results"][0]  # İlk sonucu al

        name = f"{fk['name']['title']} {fk['name']['first']} {fk['name']['last']}"  # İsim
        address = (
            f"{fk['location']['street']['number']} {fk['location']['street']['name']}"  # Adres
        )
        city = fk["location"]["city"]  # Şehir
        state = fk["location"]["state"]  # Eyalet
        country = fk["location"]["country"]  # Ülke
        postal = fk["location"]["postcode"]  # Posta kodu
        email = fk["email"]  # E-posta
        phone = fk["phone"]  # Telefon
        picture = fk["picture"]["large"]  # Resim
        gender = fk["gender"]  # Cinsiyet

        fkinfo = f"""
**İsim** ⇢ `{name}`
**Cinsiyet** ⇢ `{gender}`
**Adres** ⇢ `{address}`
**Ülke** ⇢ `{country}`
**Şehir** ⇢ `{city}`
**Eyalet** ⇢ `{state}`
**Posta Kodu** ⇢ `{postal}`
**E-posta** ⇢ `{email}`
**Telefon** ⇢ `{phone}`

        """

        await message.reply_photo(photo=picture, caption=fkinfo)  # Resmi ve bilgileri gönder
    else:
        await message.reply_text("Oops, herhangi bir adres bulunamadı.\nLütfen tekrar deneyin.")  # Hata mesajı


__MODULE__ = "Fᴀᴋᴇ"  # Modül adı
__HELP__ = """
/fake [ülke adı] - Rastgele adres almak için kullanılır.
"""
