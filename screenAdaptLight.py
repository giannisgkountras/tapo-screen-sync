import asyncio
import os
import pyautogui
import numpy as np
import cv2
from colorsys import rgb_to_hls

from tapo import ApiClient


async def main():
    tapo_username = os.getenv("TAPO_USERNAME")
    tapo_password = os.getenv("TAPO_PASSWORD")
    ip_address = os.getenv("IP_ADDRESS")

    client = ApiClient(tapo_username, tapo_password)
    device = await client.l530(ip_address)

    print("Turning device on...")
    await device.on()

    await device.set_brightness(100)
    prev_h = 0
    prev_s = 0
    prev_l = 0

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
        while True:

            # Capture screenshot
            screenshot = pyautogui.screenshot()

            # Convert the screenshot to a numpy array
            screenshot_np = np.array(screenshot)

            # Convert the image from RGB (PIL format) to BGR (OpenCV format)
            screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

            # Calculate the mean color
            mean_color_bgr = screenshot_cv.mean(axis=0).mean(axis=0)
            mean_color_rgb = mean_color_bgr[::-1]  # Convert BGR to RGB

            # Convert the mean color to HSL
            mean_color_normalized = (
                mean_color_rgb / 255.0
            )  # Normalize RGB values to [0, 1]
            mean_color_hls = rgb_to_hls(*mean_color_normalized)

            # Convert HLS values to the standard HSL representation
            h = int(mean_color_hls[0] * 360)  # Hue
            l = int(mean_color_hls[1] * 100)  # Lightness
            s = int(mean_color_hls[2] * 100)  # Saturation

            if abs(prev_h - h) > 5 or abs(prev_s - s) > 2:
                print(f"Changing Color")
                await set_hue_with_retry(h, s)

            if abs(prev_l - l) > 2:
                print(f"Changing Brightness")
                await device.set_brightness(l)

            prev_l = l
            prev_h = h
            prev_s = s
            await asyncio.sleep(0.001)  # Increased delay to prevent rate limiting
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
