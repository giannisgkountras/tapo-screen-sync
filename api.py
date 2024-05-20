import asyncio
import os
from fastapi import FastAPI
from pydantic import BaseModel
from tapo import ApiClient


class DeviceControlRequest(BaseModel):
    color_temperature: int
    brightness: int


app = FastAPI()


async def control_device(color_temperature: int, brightness: int):
    tapo_username = os.getenv("TAPO_USERNAME")
    tapo_password = os.getenv("TAPO_PASSWORD")
    ip_address = os.getenv("IP_ADDRESS")

    client = ApiClient(tapo_username, tapo_password)
    device = await client.l530(ip_address)

    print("Setting device color temperature and brightness...")
    await device.set_color_temperature(color_temperature)
    await device.set_brightness(brightness)


@app.post("/control-device")
async def control_device_endpoint(request: DeviceControlRequest):
    await control_device(request.color_temperature, request.brightness)
    return {
        "status": "success",
        "color_temperature": request.color_temperature,
        "brightness": request.brightness,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
