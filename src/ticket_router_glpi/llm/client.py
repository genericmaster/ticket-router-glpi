import httpx

def call_llm(model_name:str,system_prompt:str,prompt:str,model_url:str)->str:
   """creates an api connction with modelprovider using  model provider url and actual ticket and system propt conntent and gets back json response"""
   content= {
    "model": model_name,
    "think": False,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content":prompt}
      ]
     }
   
   response = httpx.post(model_url,json=content,timeout=180.0)
   return response.json()["choices"][0]["message"]["content"]