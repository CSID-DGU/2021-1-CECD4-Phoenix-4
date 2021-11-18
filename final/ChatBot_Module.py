import dialogflow
from google.api_core.exceptions import InvalidArgument
import os

class Chatbot:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ai-call-center-psmu-e586e119ee5c.json"
    
    def __init__(self):
        self.DIALOGFLOW_PROJECT_ID = 'ai-call-center-psmu'
        self.DIALOGFLOW_LANGUAGE_CODE = 'ko'
        self.text_to_be_analyzed = None
        self.SESSION_ID = "123456789"
        
    def answering(self, question):
        self.text_to_be_analyzed = question
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(self.DIALOGFLOW_PROJECT_ID, self.SESSION_ID)
        text_input = dialogflow.types.TextInput(text=self.text_to_be_analyzed, 
        language_code=self.DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)

        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
            self.question = response.query_result.query_text
            self.answer = response.query_result.fulfillment_text
            
        except InvalidArgument:
            raise