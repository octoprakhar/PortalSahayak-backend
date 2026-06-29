import asyncio
from fastapi import WebSocket,WebSocketDisconnect
class WebsocketManger:
    """
    It handles every thing regarding websockets connection.
    """
    def __init__(self):
        self.connections: dict[str,list[WebSocket]] = {}
    async def connect(self,websocket: WebSocket,job_id:str):
        """
        Takes device data, and job_id and make the connection
        """

        ## Acceps the connection
        await websocket.accept()

        ## If job id is not present create an empty list
        if job_id not in self.connections:
            self.connections[job_id] = []

        self.connections[job_id].append(websocket)
        print(f"Added connection for Job Id: {job_id}")

        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            # 5. Clean up when the frontend disconnects or closes the tab
            self.connections[job_id].remove(websocket)
            if not self.connections[job_id]:
                del self.connections[job_id]
            print(f"Removed connection for Job ID: {job_id}")

    def disconnect(self,connection):
        """
        It disconnects that specific connection
        """

    async def send(self,job_id: str, payload: dict):
        """
        It will send the message/data to each socket, whose has that 
        specific job_id
        """

        # Check if anyone is actively listening to this job_id
        if job_id in self.connections:
            # Send the text concurrently to all open connections under this job_id
            await asyncio.gather(*[ws.send_json(payload) for ws in self.connections[job_id]])
    