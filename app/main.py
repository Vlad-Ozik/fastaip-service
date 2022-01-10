import hmac, hashlib
import slack

from config import SECRET_KEY, PROJECT_ID, TOPIC_ID, SLACK_TOKEN

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.cloud import pubsub_v1


app = FastAPI()


class EventData(BaseModel):
    event: str
    character_id: str
    utc_timestap: str

    
def verify_signature(eventData: EventData, 
                     decoded_signature: str, 
                     shared_secret: str) -> bool:
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


@app.post("/{server_event}", status_code=201, response_model=EventData)
async def main(server_event: str,
               eventData: EventData,
               signature: str,
               appId: str = None, 
               accountId: int = None, 
               sessionId: int = None):
    if verify_signature(eventData, signature, SECRET_KEY):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
        
        future = publisher.publish(topic_path, str(dict(eventData)).encode("ascii"))
        print(future.result())
        return eventData
    else:
        client = slack.WebClient(token=SLACK_TOKEN)
        client.chat_postMessage(channel='#testapi', text=f'Invalid signature! {server_event, accountId, sessionId, signature, eventData}')
        raise HTTPException(status_code=400, detail="Invalid signature!")

    