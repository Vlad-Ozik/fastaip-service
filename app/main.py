import hmac, hashlib
import slack
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.cloud import pubsub_v1


app = FastAPI()


class EventData(BaseModel):
    event: str
    character_id: str
    utc_timestap: str

    
def verify_signature(eventData: EventData,decoded_signature: str,shared_secret: str):
    """Compare the signature in the message and the calculated signature from json

    Args:
        eventData (EventData): recived json object
        decoded_signature (str): signature in message
        shared_secret (str): secret key to generation signature

    Returns:
        bool: `True` if the signatures are the same, otherwise `False`
    """
    shared_secret = bytes(shared_secret, encoding='ascii')
    eventData_bytes = bytes(str(dict(eventData)), encoding='ascii')
    calculated_signature = hmac.new(shared_secret, eventData_bytes, hashlib.sha512).hexdigest()
    return hmac.compare_digest(calculated_signature, decoded_signature)


@app.post("/{server_event}")
async def main(server_event: str, 
               appId: str, 
               accountId: int, 
               sessionId: int, 
               signature: str,
               eventData: EventData):

    secret_key = os.environ['SHARED_SECRET']
    
    if verify_signature(eventData, signature, secret_key) is True:
        project_id = 'project-pub-task'
        topic_id = 'my-topic'

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_id)
        
        future = publisher.publish(topic_path, str(dict(eventData)).encode("ascii"))
        print(future.result())
    else:
        client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
        client.chat_postMessage(channel='#testapi', text=f'Invalid signature! {server_event, accountId, sessionId, signature, eventData}')
        raise HTTPException(status_code=400, detail="Invalid signature!")

    return {"eventData": eventData, "event": server_event,"appId": appId, "accountId": accountId}