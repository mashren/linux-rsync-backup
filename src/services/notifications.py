import requests
import argparse
from discord_webhook import DiscordWebhook, DiscordEmbed

colors = {
    "blue": 3447003,
    "red": 15158332,
    "green": 3066993
}

def send_discord_notification(url: str, subject: str,  username: str,message: str = None, textfile: str = None, embed_title: str = "embed title", split: bool = False, color="blue"):

    webhook = DiscordWebhook(url=url, content=subject, username=username)

    if message != None and message != "":
        embed = DiscordEmbed(color=colors[color])
        if split == True:
            message_parts = message.split(" \\n ")
            message_value = '{}'.format("\n".join(message_parts))
            embed.add_embed_field(name=embed_title, value=message_value)

        else:
            embed.add_embed_field(name=embed_title, value=message)
        # print(embed.get_embed_fields())
        webhook.add_embed(embed)
    if textfile != None and textfile != "":
        embed = DiscordEmbed(color=colors[color])
        f = open(textfile, 'r')
        file_content = f.read()
        f.close()
        embed.add_embed_field(name="textfile", value=file_content)
        webhook.add_embed(embed)
    response = webhook.execute()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", action="store", dest="subject")
    parser.add_argument("--message", action="store", dest="message")
    parser.add_argument("--embed-title", action="store",
                        dest="embed_title", default="embed title")
    parser.add_argument("--split", action="store_true",
                        default=False, dest="split")
    parser.add_argument("--username", action="store",
                        default=None, dest="username")
    parser.add_argument("--textfile", action="store",
                        default=None, dest="textfile")

    args = parser.parse_args()
    url = "https://discord.com/api/webhooks/819102715224260648/Jdz1Lobt1Qg60ZFpzNOO0cHWW_kgsSSysVMsI2iBCxXJB4s9lFywZQv5iFVPP-9WgdsO"
    send_discord_notification(
        url=url,
        subject=args.subject,
        message=args.message,
        embed_title=args.embed_title,
        split=args.split,
        username=args.username,
        textfile=args.textfile
    )


if __name__ == "__main__":
    main()
