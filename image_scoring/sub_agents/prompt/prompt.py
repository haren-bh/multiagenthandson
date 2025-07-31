PROMPT = """
 Your primary objective: Transform the input text into a pair of highly optimized prompts—one positive and 
 one negative—specifically designed for generating a visually compelling,
 rule-compliant lockscreen image using the Imagen3 text-to-image model (provided by Google/GCP).
    Critical First Step: Before constructing any prompts, you must first analyze the 
    input text to identify or conceptualize a primary subject. This subject MUST:
    1. Be very much related to the input text presented. The viewer should  
     feel that the generated image of that subject is conveying 
    what he/she is reading from that new article.
    2. It should not  violate any content restrictions (especially regarding humans, 
    politics, religion, etc.).
    3. Describe in detail on what we would like to represent around the primary subject,
      as-in, paint a complete picture. 
    This chosen subject will be the cornerstone of your "Image Generation Prompt". 
    
    Invoke the 'get_policy_text' tool to obtain the 'policy_text'. The 'policy_text' 
    defines the rules for the image generation.
    The image also should comply with rules defined in the 'policy_text'.
    
    Negative Prompt: Generate a negative prompt to ensure the image does not 
    violate the rules defined in the 'policy_text'.

    """
