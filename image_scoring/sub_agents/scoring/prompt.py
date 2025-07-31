SCORING_PROMPT = """

      "Your task is to evaluate an image based on a set of scoring rules. Follow these steps precisely:"
        "1.  First, invoke the async 'get_image' tool to load the images artifact and image_metadata. Do not try to generate the image."\
        " Wait for the image to be loaded and the response"
        "2.  Next, invoke the 'get_policy' tool to obtain the image scoring 'rules' in JSON format"
        "3.  Scoring Criteria: Carefully examine the rules in JSON string obtained in step 1. For EACH rule described within this JSON string:"
        "    a.  Strictly score the loaded image (from step 2) against each criterion mentioned in the JSON string."
        "    b.  Assign a score in a scale of 0 to 5: 5 points if the image complies with a specific criterion, or 0 point if it does not." \
             "Also specify the reason in a seperate attribute explaining the reason for assigning thew score"
        "4. An example of the computed scoring criteria is as follows: "
        "{\
          \"total_score\": 45,\
          \"scores\": {\
            \"General Guidelines\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the general guidelines for image, video, and text content.\"\
            },\
            \"Global Defaults\": {\
              \"score\": 0,\
              \"reason\": \"The image meets all the global defaults for image, video, and text content.\"\
            },\
            \"Media Type Definitions\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the media type definitions for image, video, and text content.\"\
            },\
            \"Image Specifications and Guidelines\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the image specifications and guidelines for image, video, and text content.\"\
            },\
            \"Text Specifications and Guidelines\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the text specifications and guidelines for image, video, and text content.\"\
            },\
            \"Clock Visibility\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the clock visibility specifications for image, video, and text content.\"\
            },\
            \"Notification Area\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the notification area specifications for image, video, and text content.\"\
            },\
            \"Safe Zones\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the safe zones specifications for image, video, and text content.\"\
            },\
            \"Composition Styles\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the composition styles specifications for image, video, and text content.\"\
            },\
            \"Color Scheme Definitions\": {\
              \"score\": 5,\
              \"reason\": \"The image meets all the color scheme definitions for image, video, and text content.\"\
            }\
          }\
        }"


        "Do not validate the JSON structure itself; only use its content for scoring rules. "
        "5. Compute the total_score by adding each individual score point for each rule in the JSON "
        "6. Invoke the set_score tool and pass the total_score. "

       
        "OUTPUT JSON FORMAT SPECIFICATION:\n"
        "The JSON object MUST have exactly two top-level keys:"
        "  - 'total_score': Iterate through each individual score element in the json and add those to arrive at total_score. "
        "  - 'scores': The existing rules json with a score attribute assigned to each rule and a reason attribute"
  
"""
