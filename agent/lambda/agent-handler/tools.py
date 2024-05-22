import os
import json
import boto3
from langchain.agents.tools import Tool
from urllib.parse import urlparse

bedrock = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])

class Tools:

    def __init__(self) -> None:
        print("Initializing Tools")
        self.tools = [
            Tool(
                name="Kittelson",
                func=self.kendra_search,
                description="Use this tool to answer questions about Kittelson.",
            )
        ]

    def parse_kendra_response(self, kendra_response):
        """
        Extracts the source URI from document attributes in Kendra response.
        """
        modified_response = kendra_response.copy()

        result_items = modified_response.get('ResultItems', [])

        for item in result_items:
            source_uri = None
            if item.get('DocumentAttributes'):
                print(f"item = {str(item)}")
                for attribute in item['DocumentAttributes']:
                    if attribute.get('Key') == '_source_uri':
                        source_uri = attribute.get('Value', {}).get('StringValue', '')

            if source_uri:
                print(f"source_uri = {source_uri}")
                item['_source_uri'] = source_uri

        return modified_response

    def kendra_search(self, question):
        """
        Performs a Kendra search using the Query API.
        This data is also going to be enriched with entity classification via comprehend.
        """
        kendra = boto3.client('kendra')

        kendra_response = kendra.query(
            IndexId=os.getenv('KENDRA_INDEX_ID'),
            QueryText=question,
            PageNumber=1,
            PageSize=5  # Limit to 5 results
        )

        parsed_results = self.parse_kendra_response(kendra_response)

        print(f"parsed_results = {parsed_results}")

        # passing in the original question, and various Kendra responses as context into the LLM
        return self.invokeLLM(question, parsed_results)

    def invokeLLM(self, question, context):
        """
        Generates an answer for the user based on the Kendra response.
        """
        prompt_data = f"""
        Human:
        Imagine you are Kittelson and Associates traffic engineering AI assistant. You respond quickly and friendly to questions from a user, providing both an answer and the sources used to find that answer.

        At the end of your response, with a break after the initial response,  include the relevant sources if information from specific sources was used in your response. Use the following format for each of the sources used: [Source #: Source Link - Page _excerpt_page_number]. This must be formatted to remove any url encoding and include the full link to the source by removing the leading S3 location and the enterprise-search-poc-57447 prefix and replacing it with a network drive H:\ prefix with a windows directory format, i.e. H:/projects/30/30344 - Newton NC SS4A Application/admin/p/City of Newton SS4A Grant Application - Kittelson.pdf. The excerpt_page_number should be formated as simply the number i.e. Page 20 .
        
        Projects are a key part of Kittelson's work. 
        
        For questions about specific projects, use the projects_data data source from the kendra response as the main context. For general questions, use the general_data data source from the kendra response.


        Using the following context, answer the following question to the best of your ability. Do not include information that is not relevant to the question, and only provide information based on the context provided without making assumptions.
        If the context is empty, please include "No sources used." and answer the question to the best of your ability, with the caveat that you are using your own infomration sources. Format your response for enhanced human readability, ensuring that proper spacing is provided between thoughts, and proper html is provided. 

        Question: {question}

        Context: {context}

        \n\nAssistant:
        """

        # Formatting the prompt as a JSON string
        json_prompt = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_data
                        }
                    ]
                }
            ]
        })

        # Invoking Claude3, passing in our prompt
        response = bedrock.invoke_model(
            body=json_prompt,
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json",
            contentType="application/json"
        )

        # Getting the response from Claude3 and parsing it to return to the end user
        response_body = json.loads(response['body'].read())
        answer = response_body['content'][0]['text']

        return answer

# Pass the initialized retriever and llm to the Tools class constructor
tools = Tools().tools
