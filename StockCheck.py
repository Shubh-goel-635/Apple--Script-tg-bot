import asyncio
from datetime import datetime

import aiohttp

from StopSignal import stop_event

STORES_PIN_CODE = [
    110017,
    560092
]

PRODUCTS = [
    {'name': 'iphone 17', 'codes': ['MG6M4HN/A', 'MG6N4HN/A', 'MG6L4HN/A', 'MG6K4HN/A', 'MG6J4HN/A']},
    # {'name': 'iphone 16', 'codes': ['MYEC3HN/A', 'MYED3HN/A', 'MYEA3HN/A', 'MYE93HN/A', 'MYE73HN/A']}
]


async def productAvailabilityCheck(session, queue):
    for pincode in STORES_PIN_CODE:
        if stop_event.is_set():
            return  # stop immediately

        for product in PRODUCTS:
            if stop_event.is_set():
                return

            product_name = product['name']
            product_codes = product['codes']

            for code in product_codes:
                if stop_event.is_set():
                    return

                url = f"https://www.apple.com/in/shop/pickup-message-recommendations?fae=true&mts.0=regular&location={pincode}&product={code}"
                try:
                    async with session.get(url, timeout=10) as response:
                        data = await response.json()

                    stores = data.get("body", {}).get("PickupMessage", {}).get("stores", [])
                    stock = []

                    for store in stores:
                        store_name = f"Apple {store.get('storeName', '')} - {pincode}"
                        store_number = store.get("storeNumber")
                        parts = store.get("partsAvailability", {})
                        product_list = []

                        for c, details in parts.items():
                            if c in product_codes:
                                name = details.get("messageTypes", {}).get("regular", {}).get(
                                    "storePickupProductTitle", product_name
                                )
                                product_list.append(name)

                        if product_list:
                            stock.append({'store_name': store_name, 'product_list': product_list})

                    if stock:
                        ist_time = datetime.now().strftime("%H:%M")
                        message_lines = ["📦 *STOCK AVAILABLE!*", f"⏰ Time: {ist_time}\n"]

                        for s in stock:
                            message_lines.append(f"🏬 *{s['store_name']}*")
                            message_lines.append("📱 Products:")
                            message_lines.extend(f"• {p}" for p in s['product_list'])
                            message_lines.append("")

                        message = "\n".join(message_lines)
                        print(message)
                        await queue.put(message)

                except Exception as e:
                    print(e)
                    await queue.put("❌ Error occurred.")
                    await queue.put(f"❌ Error: {e}")
                    stop_event.set()  # stop everything
                    return
                await asyncio.sleep(1)


async def product_stock_loop(queue):
    count = 1;
    async with aiohttp.ClientSession() as session:
        while not stop_event.is_set():
            print(f'called {count}')
            count += 1
            await productAvailabilityCheck(session, queue)
            await asyncio.sleep(1)
