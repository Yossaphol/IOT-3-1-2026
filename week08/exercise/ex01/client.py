import asyncio
import sys
import aiocoap


SERVER_IP = "172.20.10.2"
SERVER_PORT = 5683


async def send_brightness(brightness):

    protocol = await aiocoap.Context.create_client_context()

    request = aiocoap.Message(
        code=aiocoap.Code.PUT,
        uri=f"coap://{SERVER_IP}:{SERVER_PORT}/led",
        payload=str(brightness).encode()
    )

    print(f"Sending brightness = {brightness}")

    try:
        response = await protocol.request(request).response

        print(
            "Response:",
            response.code,
            response.payload.decode()
        )

    except Exception as e:
        print("Error:", e)

    finally:
        await protocol.shutdown()


async def main():

    while True:

        value = input("Enter brightness (0-100) or q to quit: ")

        if value.lower() == "q":
            break

        try:
            brightness = int(value)

            if brightness < 0 or brightness > 100:
                print("Please enter a value between 0 and 100")
                continue

            await send_brightness(brightness)

        except ValueError:
            print("Please enter a number between 0 and 100")


if __name__ == "__main__":
    asyncio.run(main())