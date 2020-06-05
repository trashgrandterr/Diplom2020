from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
import yaml
import io
import sys 
from ruamel.yaml import YAML 
import subprocess
import os





def generate(request):
    platformEndpoint = ""

    if request.method == 'POST':
        platform = request.POST['platform']

        if (platform == "azure"):
            inp_fo = open("data.yml").read()  
            yaml = YAML() 
            code = yaml.load(inp_fo) 

            serverLocation = request.POST['serverLocation']
            monthsReceipt = request.POST['monthsReceipt']
            subscriptionId = request.POST['subscriptionId']
            tenant = request.POST['tenant']
            name = request.POST['name']
            password = request.POST['password']
            token = request.POST['token']
            tax_gov = request.POST['tax_gov']
            phone = request.POST['phone']
            email = request.POST['email']
            botname = request.POST['botname']

            code['provider']['region'] = serverLocation
            code['provider']['environment']['MONTHS'] = monthsReceipt
            code['provider']['environment']['TOKEN'] = token 
            code['provider']['environment']['YOUR_PHONE'] = phone
            code['provider']['environment']['YOUR_GOV_PASS'] = tax_gov

            inp_fo = open("bot/serverless.yml").read()  
            yaml.dump(code,inp_fo) 
            inp_fo.close() 

            currentFolder = os.path.dirname(os.path.realpath(__file__)) 
            process = subprocess.Popen(['sls deploy', ], stdout=subprocess.PIPE, cwd = currentFolder, shell=True, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                return_code = process.poll()
                if return_code is not None:
                    for output in process.stdout.readlines():
                        if output.startswith("  POST"):
                            platformEndpoint = output[9:]
                    break
            
            #Setting webhook
            webhook = 'https://api.telegram.org/bot{tokenF}/setWebhook?url={endpoint}'.format(tokenF = token, endpoint = platformEndpoint)
            requests.get(webhook)

        elif (platform == "aws"):
            inp_fo = open("data.yml").read()  
            yaml = YAML() 
            code = yaml.load(inp_fo) 

            serverLocation = request.POST['serverLocation']
            monthsReceipt = request.POST['monthsReceipt']
            accessID = request.POST['accessID']
            secretKey = request.POST['secretKey']
            token = request.POST['token']
            tax_gov = request.POST['tax_gov']
            phone = request.POST['phone']
            email = request.POST['email']
            botname = request.POST['botname']

            code['provider']['region'] = serverLocation
            code['provider']['environment']['MONTHS'] = monthsReceipt
            code['provider']['environment']['TOKEN'] = token 
            code['provider']['environment']['YOUR_PHONE'] = phone
            code['provider']['environment']['YOUR_GOV_PASS'] = tax_gov

            inp_fo = open("bot/serverless.yml").read()  
            yaml.dump(code,inp_fo) 
            inp_fo.close() 

            currentFolder = os.path.dirname(os.path.realpath(__file__)) 
            process = subprocess.Popen(['sls deploy', ], stdout=subprocess.PIPE, cwd = currentFolder, shell=True, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                return_code = process.poll()
                if return_code is not None:
                    for output in process.stdout.readlines():
                        if output.startswith("  POST"):
                            platformEndpoint = output[9:]
                    break
            
            #Setting webhook
            webhook = 'https://api.telegram.org/bot{tokenF}/setWebhook?url={endpoint}'.format(tokenF = token, endpoint = platformEndpoint)
            requests.get(webhook)

        elif (platform == "aws"):
            inp_fo = open("bot/serverless.yml").read()  
            yaml = YAML() 
            code = yaml.load(inp_fo) 

            serverLocation = request.POST['serverLocation']
            monthsReceipt = request.POST['monthsReceipt']
            accessID = request.POST['accessID']
            secretKey = request.POST['secretKey']
            token = request.POST['token']
            tax_gov = request.POST['tax_gov']
            phone = request.POST['phone']
            email = request.POST['email']
            botname = request.POST['botname']

            code['provider']['region'] = serverLocation
            code['provider']['environment']['MONTHS'] = monthsReceipt
            code['provider']['environment']['TOKEN'] = token 
            code['provider']['environment']['YOUR_PHONE'] = phone
            code['provider']['environment']['YOUR_GOV_PASS'] = tax_gov

 
            inp_fo = open("bot/serverless.yml").read()  
            yaml.dump(code,inp_fo) 
            inp_fo.close() 

            currentFolder = os.path.dirname(os.path.realpath(__file__)) 
            process = subprocess.Popen(['sls deploy', ], stdout=subprocess.PIPE, cwd = currentFolder, shell=True, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                return_code = process.poll()
                if return_code is not None:
                    for output in process.stdout.readlines():
                        if output.startswith("  POST"):
                            platformEndpoint = output[9:]
                    break
            
            #Setting webhook
            webhook = 'https://api.telegram.org/bot{tokenF}/setWebhook?url={endpoint}'.format(tokenF = token, endpoint = platformEndpoint)
            requests.get(webhook)
        return redirect('success')
    else:
        return render(request, 'botgeneration/generateBot.html')


def success(request):
    return render(request, 'botgeneration/success.html')


def sms(request):
    if request.method == 'POST':
        your_phone = request.POST['phone']
        email = request.POST['email']
        nickname = request.POST['nickname']
        r = requests.post('https://proverkacheka.nalog.ru:9999/v1/mobile/users/signup', json = {"email":email,"name":nickname,"phone":your_phone})
        return redirect('generate')
    return render(request, 'botgeneration/sms.html')




