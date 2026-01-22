import os
import logging
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureClient:
    """
    Wrapper for interactions with Azure OpenAI Service.
    """
    def __init__(self):
        # ------------------------------------------------------------------
        # AZURE CONFIGURATION (USER MUST FILL THIS IN)
        # ------------------------------------------------------------------
        # Replace these placeholders with your actual Azure details.
        # You can also use environment variables if you prefer.
        
        # The API key for your Azure OpenAI resource.
        self.api_key = "YOUR_AZURE_OPENAI_API_KEY" 
        
        # The base URL for your Azure OpenAI resource (e.g., "https://<your-resource-name>.openai.azure.com/")
        self.azure_endpoint = "https://YOUR_RESOURCE_NAME.openai.azure.com/"
        
        # The API version you want to use (e.g., "2024-02-15-preview")
        self.api_version = "2024-02-15-preview"
        
        # The name of your deployed model in Azure AI Studio (e.g., "gpt-35-turbo" or "my-custom-model")
        self.deployment_name = "YOUR_DEPLOYMENT_NAME"
        # ------------------------------------------------------------------

        # Initialize the Azure client
        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint
            )
            logger.info("AzureOpenAI client initialized locally.")
        except Exception as e:
            logger.error(f"Failed to initialize AzureOpenAI client: {e}")
            self.client = None

    def generate(self, prompt: str, max_tokens: int = 256) -> dict:
        """
        Send a prompt to the Azure OpenAI model and return the response.
        Matches the interface used by other clients (like MistralClient).
        """
        if not self.client:
            return {"error": "Azure Client not initialized. Check credentials."}

        try:
            # Call the specific deployment
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )

            # Extract the content from the response
            # Usage: response.choices[0].message.content
            if response.choices:
                content = response.choices[0].message.content
                logger.info("Azure response received successfully.")
                return {"response": content}
            else:
                return {"error": "Empty response from Azure."}

        except Exception as e:
            logger.error(f"Azure API Call Failed: {e}")
            return {"error": str(e)}

    def test_connection(self):
        """
        Simple test method to verify connectivity to Azure.
        """
        print("--- Testing Azure Connection ---")
        if self.api_key == "YOUR_AZURE_OPENAI_API_KEY":
             print("❌ API Key is still the placeholder. Please edit this file and add your key.")
             return

        result = self.generate("Hello, are you connected?")
        
        if "error" in result:
            print(f"❌ Connection Failed: {result['error']}")
        else:
            print("✅ Connection Successful!")
            print(f"Received Response: {result['response']}")

if __name__ == "__main__":
    # When running this file directly, test the connection
    client = AzureClient()
    client.test_connection()
