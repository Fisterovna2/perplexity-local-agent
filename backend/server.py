import asyncio
import json
import pyautogui
import chromadb
import time
import websockets
from agent_core import (
    analyzescreendatamultimonitor,
    comparescreenssemantics,
    checkgoalcompleted,
    construct_agent_prompt
)


# Настройка ChromaDB
CHROMA_CLIENT = chromadb.PersistentClient(path="./agent_memory_db")
MEMORY = CHROMA_CLIENT.get_or_create_collection("agent_memory")


async def run_loop(websocket, goal, role):
    session = {'action_history': [], 'screen_changed': True, 'is_active': True}
    last_img = ""
    
    # Извлекаем память под конкретную роль
    memory_results = MEMORY.query(query_texts=[f"{role} {goal}"], n_results=2)
    memory_ctx = str(memory_results['documents']) if memory_results['documents'] else "Опыта нет."


    for step in range(30):
        if not session['is_active']: break
        
        vision = analyzescreendatamultimonitor(goal)
        current_img = vision.get('screenshot_b64', "")
        session['screen_changed'] = comparescreenssemantics(last_img, current_img)
        
        is_done, reason = await checkgoalcompleted(goal, vision, session['action_history'])
        if is_done:
            await websocket.send(json.dumps({"type": "success", "content": f"Цель достигнута: {reason}"}))
            MEMORY.add(documents=[goal], metadatas=[{"role": role, "success": True}], ids=[f"id_{time.time()}"])
            break


        prompt = construct_agent_prompt(goal, memory_ctx, vision, session, role)
        
        # Вызов LLM
        import requests
        resp = requests.post("http://localhost:11434/api/generate", json={"model": "llama3", "prompt": prompt, "stream": False})
        cmd_raw = resp.json().get('response', '')
        
        # Выполнение (упрощенно)
        if "<COMMAND>" in cmd_raw:
            cmd = cmd_raw.split("<COMMAND>")[1].split("</COMMAND>")[0].strip()
            # Здесь логика pyautogui (click, type, etc)
            session['action_history'].append(cmd)
            await websocket.send(json.dumps({"type": "status", "step": step, "action": cmd, "role": role}))
        
        last_img = current_img
        await asyncio.sleep(1)


async def handler(websocket):
    async for msg in websocket:
        data = json.loads(msg)
        if data['type'] == 'start_task':
            # Ожидаем роль из UI, иначе универсал
            role = data.get('role', 'universal')
            asyncio.create_task(run_loop(websocket, data['goal'], role))


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
