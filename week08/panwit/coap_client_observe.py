import asyncio
from aiocoap import Context, Message
import aiocoap


async def main():

    protocol = await Context.create_client_context()

    request = Message(
        code=aiocoap.Code.GET,
        uri="coap://127.0.0.1:5683/temperature"
    )

    # เริ่ม Observe
    request.opt.observe = 0

    requester = protocol.request(request)

    # รับ Response แรก
    response = await requester.response

    print("Temperature:", response.payload.decode())

    # รับ Notification ต่อ ๆ ไป
    async for response in requester.observation:

        print(
            "Temperature:",
            response.payload.decode()
        )


asyncio.run(main())