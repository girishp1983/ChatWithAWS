#pip install -r requirements.txt


import sys
import os
import openai
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import subprocess

load_dotenv()

openai.api_key = os.environ['openaikey']
aws_access_key_id = os.environ['accesskey']
aws_secret_access_key = os.environ['secretkey']
region = os.environ['region']

def main():
    if len(sys.argv) < 2:
        print("Usage: python aws_query_v2.py <simple_english_query>")
        sys.exit(1)

    boto3.setup_default_session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )

    query = " ".join(sys.argv[1:])
    command = convert_to_aws_command(query)

    if command:
        handle_command(command, query)
    else:
        print("Could not convert the query to an AWS command. Please try again.")



def convert_to_aws_command(query):
    prompt = f"Imagine you are helping me conver my requirements to deal with AWS cloud into AWS CLI command. Try to figure out what service I am trying to deal with. Sometimes I will use shorthand to describe AWS service name. For example, I could refer Relational Database Management system as RDS. Come up with a AWS CLI command to requested details for the resource type I am referring to. Use --filter where necessary. Here is my query: {query}"

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.0,
    )

    command_returned = response.choices[0].text.strip()
    print("Returned command")
    print(command_returned)
    # Replace any spaces inside square brackets with no space
    command = command_returned.replace(', ', ',')
    command = command.replace("'", "")
    command = command.replace('"', '')
    print("Cleaned command")
    print(command)

    if command.startswith("aws"):
        #print("Command to be executed")
        #print (command)
        return command
    else:
        return None

def handle_command(command, query):
    try:
        #print(f"Executing AWS CLI command: {command}")
        #print(command.split())
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            print("Command output:")
            print(output.decode("utf-8"))
        else:
            print("Command error:")
            print(error.decode("utf-8"))

    except Exception as e:
        print(f"Error executing the command: {e}")

    #with open(output.decode("utf-8"), "r") as f:
    context = output.decode("utf-8")
    #prompt = "Get information about EC2 instances"
    prompt = query
    #print (query)
    answer = answer_specifically(prompt, context)
    print ("answer_specifically")
    print(answer)

def answer_specifically (prompt, context):

    newprompt = f"Given following data from AWS, please answer my question. Please formulate the response in form of an english statement, please do not formulate as a table even though the question may ask for it. Data: {context} Question: {prompt}  "  
    #print (newprompt)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt= newprompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.0,
    )

    #command = response.choices[0].text.strip()
    #print ("Specific answer")
    #print (response.choices[0].text.strip())

    return response.choices[0].text.strip()

if __name__ == "__main__":
    main()