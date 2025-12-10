# """Azure OpenAI Service - Handles chat completions and RAG"""
# import requests
# import json
# from typing import List, Dict, Optional, Generator
# from config import Config
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class OpenAIService:
#     """Service for managing Azure OpenAI chat completions"""
    
#     def __init__(self, config: Config):
#         """
#         Initialize OpenAI Service
        
#         Args:
#             config: Configuration object with Azure credentials
#         """
#         self.config = config
#         self.messages: List[Dict[str, str]] = []
#         self.data_sources: List[Dict] = []
        
#         # Sentence-level punctuation for streaming
#         self.sentence_punctuations = ['.', '?', '!', ':', ';', '。', '?', '!', ':', ';']
    
#     def add_system_message(self, content: str):
#         """Add system message to conversation"""
#         if not self.data_sources:  # Only add system message if not using data sources
#             self.messages.append({
#                 "role": "system",
#                 "content": content
#             })
#             logger.info("System message added")
    
#     def add_user_message(self, content: str):
#         """Add user message to conversation"""
#         self.messages.append({
#             "role": "user",
#             "content": content
#         })
#         logger.info(f"User message added: {content[:50]}...")
    
#     def add_assistant_message(self, content: str):
#         """Add assistant message to conversation"""
#         self.messages.append({
#             "role": "assistant",
#             "content": content
#         })
#         logger.info(f"Assistant message added: {content[:50]}...")
    
#     def clear_messages(self):
#         """Clear all messages"""
#         self.messages = []
#         logger.info("Messages cleared")
    
#     def set_data_sources(
#         self,
#         endpoint: str,
#         api_key: str,
#         index_name: str,
#         role_information: str
#     ):
#         """
#         Configure Azure Cognitive Search data source for RAG
        
#         Args:
#             endpoint: Azure Cognitive Search endpoint
#             api_key: Azure Cognitive Search API key
#             index_name: Index name
#             role_information: System prompt/role information
#         """
#         self.data_sources = [{
#             "type": "AzureCognitiveSearch",
#             "parameters": {
#                 "endpoint": endpoint,
#                 "key": api_key,
#                 "indexName": index_name,
#                 "semanticConfiguration": "",
#                 "queryType": "simple",
#                 "fieldsMapping": {
#                     "contentFieldsSeparator": "\n",
#                     "contentFields": ["content"],
#                     "filepathField": None,
#                     "titleField": "title",
#                     "urlField": None
#                 },
#                 "inScope": True,
#                 "roleInformation": role_information
#             }
#         }]
#         logger.info(f"Data sources configured: {index_name}")
    
#     def get_chat_response(self, user_query: str) -> str:
#         """
#         Get chat response from Azure OpenAI (non-streaming)
        
#         Args:
#             user_query: User's query text
            
#         Returns:
#             str: Assistant's response
#         """
#         self.add_user_message(user_query)
        
#         try:
#             # Construct URL
#             if self.data_sources:
#                 url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/extensions/chat/completions?api-version={self.config.openai_api_version}"
#             else:
#                 url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/chat/completions?api-version={self.config.openai_api_version}"
            
#             # Prepare request body
#             body = {
#                 "messages": self.messages,
#                 "stream": False
#             }
            
#             if self.data_sources:
#                 body["dataSources"] = self.data_sources
            
#             # Make request
#             headers = {
#                 "api-key": self.config.openai_key,
#                 "Content-Type": "application/json"
#             }
            
#             response = requests.post(url, headers=headers, json=body)
#             response.raise_for_status()
            
#             result = response.json()
            
#             # Extract response
#             if self.data_sources:
#                 # With data sources, response structure is different
#                 assistant_reply = ""
#                 for choice in result.get("choices", []):
#                     for message in choice.get("messages", []):
#                         if message.get("role") == "assistant":
#                             content = message.get("content", "")
#                             # Remove document references like [doc1]
#                             import re
#                             content = re.sub(r'\[doc\d+\]', '', content).strip()
#                             assistant_reply += content
#             else:
#                 assistant_reply = result["choices"][0]["message"]["content"]
            
#             self.add_assistant_message(assistant_reply)
            
#             return assistant_reply
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error getting chat response: {e}")
#             if hasattr(e, 'response') and e.response is not None:
#                 logger.error(f"Response: {e.response.text}")
#             raise
    
#     def get_chat_response_stream(self, user_query: str) -> Generator[str, None, None]:
#         """
#         Get streaming chat response from Azure OpenAI
        
#         Args:
#             user_query: User's query text
            
#         Yields:
#             str: Chunks of assistant's response
#         """
#         self.add_user_message(user_query)
        
#         try:
#             # Construct URL
#             if self.data_sources:
#                 url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/extensions/chat/completions?api-version={self.config.openai_api_version}"
#             else:
#                 url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/chat/completions?api-version={self.config.openai_api_version}"
            
#             # Prepare request body
#             body = {
#                 "messages": self.messages,
#                 "stream": True
#             }
            
#             if self.data_sources:
#                 body["dataSources"] = self.data_sources
            
#             # Make streaming request
#             headers = {
#                 "api-key": self.config.openai_key,
#                 "Content-Type": "application/json"
#             }
            
#             response = requests.post(url, headers=headers, json=body, stream=True)
#             response.raise_for_status()
            
#             assistant_reply = ""
#             tool_content = ""
            
#             # Process streaming response
#             for line in response.iter_lines():
#                 if line:
#                     line_text = line.decode('utf-8')
                    
#                     if line_text.startswith('data: ') and not line_text.endswith('[DONE]'):
#                         try:
#                             json_str = line_text[6:]  # Remove 'data: ' prefix
#                             chunk = json.loads(json_str)
                            
#                             # Extract content based on whether using data sources
#                             if self.data_sources:
#                                 # With data sources
#                                 for choice in chunk.get("choices", []):
#                                     for message in choice.get("messages", []):
#                                         role = message.get("delta", {}).get("role")
#                                         if role == "tool":
#                                             tool_content = message.get("delta", {}).get("content", "")
#                                         elif role == "assistant" or role is None:
#                                             content = message.get("delta", {}).get("content", "")
#                                             if content and content != "[DONE]":
#                                                 # Remove document references
#                                                 import re
#                                                 content = re.sub(r'\[doc\d+\]', '', content)
#                                                 if content:
#                                                     assistant_reply += content
#                                                     yield content
#                             else:
#                                 # Without data sources
#                                 delta = chunk["choices"][0].get("delta", {})
#                                 content = delta.get("content", "")
#                                 if content:
#                                     assistant_reply += content
#                                     yield content
                                    
#                         except json.JSONDecodeError:
#                             continue
            
#             # Add complete response to messages
#             if tool_content:
#                 self.messages.append({
#                     "role": "tool",
#                     "content": tool_content
#                 })
            
#             self.add_assistant_message(assistant_reply)
            
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error in streaming response: {e}")
#             if hasattr(e, 'response') and e.response is not None:
#                 logger.error(f"Response: {e.response.text}")
#             raise
    
#     def get_messages(self) -> List[Dict[str, str]]:
#         """Get current message history"""
        # return self.messages.copy()

"""Azure OpenAI Service - Handles chat completions and RAG"""
import requests
import json
from typing import List, Dict, Optional, Generator
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for managing Azure OpenAI chat completions"""
    
    def __init__(self, config: Config):
        """
        Initialize OpenAI Service
        
        Args:
            config: Configuration object with Azure credentials
        """
        self.config = config
        self.messages: List[Dict[str, str]] = []
        self.data_sources: List[Dict] = []
        
        # Sentence-level punctuation for streaming
        self.sentence_punctuations = ['.', '?', '!', ':', ';', '。', '？', '！', '：', '；']
    
    def add_system_message(self, content: str):
        """Add system message to conversation"""
        if not self.data_sources:  # Only add system message if not using data sources
            self.messages.append({
                "role": "system",
                "content": content
            })
            logger.info("System message added")
    
    def add_user_message(self, content: str):
        """Add user message to conversation"""
        self.messages.append({
            "role": "user",
            "content": content
        })
        logger.info(f"User message added: {content[:50]}...")
    
    def add_assistant_message(self, content: str):
        """Add assistant message to conversation"""
        self.messages.append({
            "role": "assistant",
            "content": content
        })
        logger.info(f"Assistant message added: {content[:50]}...")
    
    def clear_messages(self):
        """Clear all messages"""
        self.messages = []
        logger.info("Messages cleared")
    
    def set_data_sources(
        self,
        endpoint: str,
        api_key: str,
        index_name: str,
        role_information: str
    ):
        """
        Configure Azure Cognitive Search data source for RAG
        
        Args:
            endpoint: Azure Cognitive Search endpoint
            api_key: Azure Cognitive Search API key
            index_name: Index name
            role_information: System prompt/role information
        """
        self.data_sources = [{
            "type": "azure_search",
            "parameters": {
                "endpoint": endpoint,
                "authentication": {
                    "type": "api_key",
                    "key": api_key
                },
                "index_name": index_name,
                "query_type": "simple",
                "in_scope": True,
                "role_information": role_information
            }
        }]
        logger.info(f"Data sources configured: {index_name}")
    
    def get_chat_response(self, user_query: str) -> str:
        """
        Get chat response from Azure OpenAI (non-streaming)
        
        Args:
            user_query: User's query text
            
        Returns:
            str: Assistant's response
        """
        self.add_user_message(user_query)
        
        try:
            # Construct URL - use extensions only if data sources are configured
            if self.data_sources:
                # Use 2024-02-15-preview API version for extensions
                url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/extensions/chat/completions?api-version=2024-02-15-preview"
            else:
                # Use standard chat completions endpoint
                url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/chat/completions?api-version=2024-08-01-preview"
            
            # Prepare request body
            body = {
                "messages": self.messages,
                "stream": False,
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            if self.data_sources:
                body["data_sources"] = self.data_sources
            
            # Make request
            headers = {
                "api-key": self.config.openai_key,
                "Content-Type": "application/json"
            }
            
            logger.info(f"Calling URL: {url}")
            logger.info(f"Using data sources: {bool(self.data_sources)}")
            
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            # Log response for debugging
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code}")
                logger.error(f"Response: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response
            if self.data_sources:
                # With data sources, response structure may differ
                assistant_reply = ""
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice:
                        assistant_reply = choice["message"].get("content", "")
                    elif "messages" in choice:
                        for message in choice["messages"]:
                            if message.get("role") == "assistant":
                                content = message.get("content", "")
                                # Remove document references like [doc1]
                                import re
                                content = re.sub(r'\[doc\d+\]', '', content).strip()
                                assistant_reply += content
            else:
                assistant_reply = result["choices"][0]["message"]["content"]
            
            self.add_assistant_message(assistant_reply)
            
            return assistant_reply
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting chat response: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            
            # Return a user-friendly error message
            error_msg = "I apologize, but I'm having trouble connecting to the AI service. Please check your configuration."
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 404:
                    error_msg = "Deployment not found. Please verify your Azure OpenAI deployment name in the .env file."
                elif e.response.status_code == 401:
                    error_msg = "Authentication failed. Please check your API key in the .env file."
                elif e.response.status_code == 429:
                    error_msg = "Rate limit exceeded. Please wait a moment and try again."
            
            return error_msg
    
    def get_chat_response_stream(self, user_query: str) -> Generator[str, None, None]:
        """
        Get streaming chat response from Azure OpenAI
        
        Args:
            user_query: User's query text
            
        Yields:
            str: Chunks of assistant's response
        """
        self.add_user_message(user_query)
        
        try:
            # Construct URL
            if self.data_sources:
                url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/extensions/chat/completions?api-version=2024-02-15-preview"
            else:
                url = f"{self.config.openai_endpoint}/openai/deployments/{self.config.openai_deployment}/chat/completions?api-version=2024-08-01-preview"
            
            # Prepare request body
            body = {
                "messages": self.messages,
                "stream": True,
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            if self.data_sources:
                body["data_sources"] = self.data_sources
            
            # Make streaming request
            headers = {
                "api-key": self.config.openai_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=body, stream=True, timeout=30)
            response.raise_for_status()
            
            assistant_reply = ""
            tool_content = ""
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    
                    if line_text.startswith('data: ') and not line_text.endswith('[DONE]'):
                        try:
                            json_str = line_text[6:]  # Remove 'data: ' prefix
                            chunk = json.loads(json_str)
                            
                            # Extract content based on whether using data sources
                            if self.data_sources:
                                # With data sources
                                for choice in chunk.get("choices", []):
                                    delta = choice.get("delta", {})
                                    content = delta.get("content", "")
                                    if content and content != "[DONE]":
                                        # Remove document references
                                        import re
                                        content = re.sub(r'\[doc\d+\]', '', content)
                                        if content:
                                            assistant_reply += content
                                            yield content
                            else:
                                # Without data sources
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    assistant_reply += content
                                    yield content
                                    
                        except json.JSONDecodeError:
                            continue
            
            # Add complete response to messages
            self.add_assistant_message(assistant_reply)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in streaming response: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get current message history"""
        return self.messages.copy()