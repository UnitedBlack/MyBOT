from TrashCan.main_test import parse_main_page
import asyncio

async def bebra():
    await parse_main_page()
    
    
asyncio.run(bebra())