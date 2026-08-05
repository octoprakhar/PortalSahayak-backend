import asyncio
from fastapi import WebSocket,WebSocketDisconnect
import logging
class WebsocketManger:
    """
    It handles every thing regarding websockets connection.
    """
    def __init__(self):
        self.connections: dict[str,list[WebSocket]] = {}
    async def connect(self,websocket: WebSocket,user_id:str):
        """
        Takes device data, and job_id and make the connection
        """

        ## Acceps the connection
        await websocket.accept()

        ## If job id is not present create an empty list
        if user_id not in self.connections:
            self.connections[user_id] = []

        self.connections[user_id].append(websocket)
        print(f"Added connection for Job Id: {user_id}")

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            # 5. Clean up when the frontend disconnects or closes the tab
            self.connections[user_id].remove(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
            print(f"Removed connection for Job ID: {user_id}")

    def disconnect(self,connection):
        """
        It disconnects that specific connection
        """

    async def send(self,user_id: str, payload: dict):
        """
        It will send the message/data to each socket, whose has that 
        specific job_id
        """

        # Check if anyone is actively listening to this job_id
        # logging.info("Entered websocket.send")
        if user_id in self.connections:
            # Send the text concurrently to all open connections under this job_id
            # logging.info(f"About to send message: to userId: {user_id}, and payload: {payload}")
            await asyncio.gather(*[ws.send_json(payload) for ws in self.connections[user_id]])
            # logging.info("Send completed")
    