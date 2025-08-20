import os
from google import genai
from google.genai import types

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

GEMINI_API_KEY = os.getenv("api_key")


client = genai.Client(api_key=GEMINI_API_KEY)


class requirements(BaseModel):
    score: float = Field(description="The overall score of the essay")
    TR_score : float = Field(description="The score of TR part")
    LR_score : float = Field(description="The score of LR part")
    CC_score : float = Field(description="The score of CC part")
    GRA_score : float = Field(description="The score of GRA part")

generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        thinking_budget=-1,
    ),
    media_resolution="MEDIA_RESOLUTION_MEDIUM",
    response_mime_type="application/json",
    response_schema=requirements,
    system_instruction="""You are an IELTS examiner. I will submit my essay, and you will give it a score and briefly point out any issues."""
)

input = f"""In some countries, the number of people visiting art galleries is reducing. What are the reasons for this? How can we solve this problem?

In contemporary society, the trend of visiting art galleries is becoming less popular. Multiple factors such as living rhythm, social economic or aesthetic alterations can illustrate this phenomenon. 

Living in the fast-paced modern society, people emphasis more on efficiency, whether in workplace or entertainment. The emergence of internet accelerates this thinking tendency, which implies the long-term indulgence in shallow pleasures has gradually deprived us of the ability to think and appreciate more deeply. Controversy to modern pace, the appreciation of artworks requires a more profound reflecting and understanding, leading to the reduce of gallery’s visit. Moreover, economic pressure on individuals can significantly reduce people’s desire to visit. Furthermore, the change on social aesthetics cannot be neglected. For instance, affected by commercial products or other factors, people nowadays are more inclined to watch minimalist works. However, the art galleries possess a variety type of artworks, from simplism to impressionism. The homogenization of aesthetics makes visitors difficult to accept diverse styles.

To ameliorate the attendance of art galleries, some improvements can take into consideration. Primarily, intensify publicity efforts is indispensable to attract visitors, this approach is equally significant for cultural dissemination, which inspires people’s interest to visit. The price can have some changes like giving discount to increase the affordability of visitors. Finally, the combination with social platforms could be effective to adapt and integrate with modern individual’s life and reducing the gap between art and ordinary people. 

In conclusion, the decline of visiting numbers of art galleries is the result of multiple factors, including social or financial aspects. Therefore, a more flexible adaptation is vital to improve the popularity of art. Resolutions such as improving advocation, adjusting prices or integrating with media are ensure the sustainability of art gallery’s development.
In recent years, the number of people visiting galleries has experienced an obvious decline in some countries, which has drawn people's attention and caused some concerns. There are complicated reasons behind this phenomenon, the top two of which are as follows.

"""

response = client.models.generate_content(
    model="gemini-2.5-flash", 
    contents=input,
    config=generate_content_config
)
if response.text:
    parsed_response = requirements.model_validate_json(response.text)
    print(f"分数: {parsed_response.score}")
    print(f"TR: {parsed_response.TR_score}, LR:{parsed_response.LR_score}, CC:{parsed_response.CC_score}, GRA:{parsed_response.GRA_score}")