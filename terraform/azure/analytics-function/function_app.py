import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", 
                               event_hub_name="analytics-topic",
                               connection="EventHubConnection") 
def analytics_trigger(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event.')
    
    event_body = azeventhub.get_body().decode('utf-8')
    
    try:
        record = json.loads(event_body)
        logging.info(f"Processing record: {record}")
        # Logic to save to Azure SQL or Blob Storage would go here
        # For assignment demo, logging the receipt is often sufficient 
        # unless you implement the Database sink.
    except Exception as e:
        logging.error(f"Error parsing event: {e}")