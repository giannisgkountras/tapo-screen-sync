import asyncio
import os

from tapo import ApiClient
from tapo.requests import Color


async def main():
    tapo_username = os.getenv("TAPO_USERNAME")
    tapo_password = os.getenv("TAPO_PASSWORD")
    ip_address = os.getenv("IP_ADDRESS")

    client = ApiClient(tapo_username, tapo_password)
    device = await client.l530(ip_address)

    print("Turning device on...")
    await device.on()

    await device.set_brightness(100)

    async def set_hue_with_retry(hue, saturation, retries=3):
        for attempt in range(retries):
            try:
                await device.set_hue_saturation(hue, saturation)
                return
            except Exception as e:
                print(f"Error setting hue to {hue} on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)  # Wait before retrying

    try:
        for i in range(1, 360):
            print(f"Setting hue to {i}")
            await set_hue_with_retry(i, 100)
            await asyncio.sleep(0.5)  # Increased delay to prevent rate limiting
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
