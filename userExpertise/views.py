from django.shortcuts import render, redirect
from .models import expertUser , Domain , Tags
from together import Together
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
import requests

def ask_domain(request):
    domains = Domain.objects.all()
    context = {
        'domains': domains
    }
    return render(request, 'userExpertise/expertise.html', context)


def ask_tags(request):
    context = {
        'tags':tags
    }
    return render(request , 'userExpertise/expertise.html',context)

def get_domain(request):
    print('hello')
    domain_name = request.GET.get('domain')
    if domain_name:
        
        print(domain_name)
        # Call the get_evalQuestions function (assumed to be defined)
        processedQuestion = get_evalQuestion(domain_name)
        
        print("/n/n/n")
        print(processedQuestion)
        structered_questions = process_quiz_data(processedQuestion)
        print("\n\n")
        # print(structered_questions)
        
        

        # Render the result or redirect as needed
        return render(request, 'userExpertise/expertise.html', {'domain': domain_name , 'questions': structered_questions})
    else:
        # Handle the case where no domain is selected
        return redirect('askDomain')  # Redirect back to the domain selection

    

def process_quiz_data(raw_data):
    def parse_code_block(lines, start_index):
        code_block = []
        i = start_index
        while i < len(lines) and lines[i] != '```':
            code_block.append(lines[i])
            i += 1
        return '\n'.join(code_block), i

    structured_quiz = {}
    current_section = None
    current_question = None
    i = 0
    
    while i < len(raw_data):
        line = raw_data[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
            
        # Handle section headers
        if line.startswith('**') and line.endswith('**'):
            current_section = line.strip('* ')
            structured_quiz[current_section] = []
            i += 1
            continue
            
        # Handle questions
        if current_section and (line[0].isdigit() and '. ' in line):
            question_text = line[line.index('.')+1:].strip()
            
            # Check if next line contains code block
            code_block = ""
            explanation = ""
            options = []
            
            next_idx = i + 1
            if next_idx < len(raw_data) and raw_data[next_idx].strip() == '```':
                # Skip the opening ```
                next_idx += 1
                code_block, end_idx = parse_code_block(raw_data[next_idx:], 0)
                i = next_idx + end_idx + 1  # Skip past the closing ```
            
            # Check for multiple choice options
            while next_idx < len(raw_data) and raw_data[next_idx].strip().startswith(('A)', 'B)', 'C)', 'D)')):
                options.append(raw_data[next_idx].strip())
                next_idx += 1
            
            question_data = {
                "question": question_text,
                "code_block": code_block if code_block else "",
                "options": options,
                "type": "multiple_choice" if options else "code_input",
                "explanation": explanation
            }
            
            structured_quiz[current_section].append(question_data)
            
            if not code_block and not options:
                i = next_idx
            
        i += 1
                
    return structured_quiz


client = Together()

def get_evalQuestion(domainName):
    
    prompt = """ 
        Create a series of questions or code based snippets as per the domain fed into the prompt .
        I just need the set of question and code snippet based question and not the answers for it.
    """

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        messages=[{'role':'system' , 'content':prompt} , {'role':'user' , 'content':domainName}],
        max_tokens=1000,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>"],
        stream=False
    )
    return response.choices[0].message.content.splitlines()


import re

def extract_percentage(text):
    # Regular expression to find the percentage
    match = re.search(r'(\d+)%', text)
    if match:
        return int(match.group(1))  # Convert matched string to integer
    return None  # Return None if no match is found


@csrf_exempt  # Use this only for testing; better to use CSRF tokens in production.
def submit_quiz(request):
    if request.method == 'POST':
        # Parse the JSON body
        body = json.loads(request.body)

        # Initialize a structured response
        structured_data = {}

        # Iterate through the incoming data
        for key, value in body.items():
            if key.startswith('question_'):
                # Extract the question type and number
                _, question_type, question_number = key.split('_', 2)
                
                # Create a structured dictionary for each question type if it doesn't exist
                if question_type not in structured_data:
                    structured_data[question_type] = {}

                # Store the question number and user's answer
                structured_data[question_type][question_number] = value

        # Send the structured data to an external API
        print("i have reached here")
        score = getScore(json.dumps(structured_data))
        print("i am here")
        
        # Extract percentage
        percentage = extract_percentage(score)
        print(f'Extracted Percentage: {percentage}%')
        
    domain_id = 1  # Replace with the actual ID or logic to get the desired domain
    try:
        domain_instance = Domain.objects.get(id=domain_id)  # Use the correct ID or filter
        domain_instance.score = percentage  # Update the score
        domain_instance.save()  # Save the changes
    except Domain.DoesNotExist:
        return JsonResponse({'error': 'Domain not found'}, status=404)
        
        print(prercentage)
        
        if score >= 75:
            user_badge  = Domain.objects.all()
            user_badge.badge = 'Expert'
            user_badge.save()
        else :
            alert('Your Score : ', score ,' is  less that 75% therefore you need to evaluate a test again on the respective domain')


    return render(request, 'userExpertise/expertise.html', {'score':score})

def getScore(structData):
    
    prompt = """ 
        The data that is been given as a prompt is in json format where the question is the key and its corresponding score is the value.
        Now what you should do is to evaluate the test such that all the answers should be highly optimized and you should score him percentage wise,
        and return the score to me accordingly. Do not give me code. Go step by step and verify the answers. Score accordingly.Do not explain 
        what is the correct answer jsut evaluate it and provide the score.
    """

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        messages=[{'role':'system' , 'content':prompt} , {'role':'user' , 'content':structData}],
        max_tokens=500,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>"],
        stream=False
    )
    return response.choices[0].message.content
   

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import expertUser, Domain  # Adjust the import based on your file structure

@login_required
@csrf_exempt
def change_badge(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        badge = body.get('badge', None)
        user = request.user

        if badge not in ['Expert', 'Novice']:
            return JsonResponse({'error': 'Invalid badge'}, status=400)

        # If user selects "Expert", verify score
        if badge == "Expert":
            sc = Domain.objects.all()
            score = sc.score  

            if score <= 75:
                return JsonResponse({'error': 'Score below threshold for Expert'}, status=403)

        # Update or create the user's badge
        expert_user, created = expertUser.objects.get_or_create(user=user)
        expert_user.badge = badge
        expert_user.save()

        return JsonResponse({'success': True, 'badge': badge})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@csrf_exempt
def verify_expert(request):
    if request.method == 'POST':
        user = request.user
        sc = Domain.objects.get(user=user) 
        score = sc.score # Replace with your logic
        is_expert = score > 75
        return JsonResponse({'is_expert': is_expert})

    return JsonResponse({'error': 'Invalid request'}, status=400)

 

                  
