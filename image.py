from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import OpenAI

import urllib.request
import dotenv

dotenv.load_dotenv()


def generate_image(description):
    llm = OpenAI(temperature=1)
    prompt = PromptTemplate(
        input_variables=["image_desc"],
        template=(
            "Generate a detailed prompt to generate an image based on the following description: {image_desc}"
        )
    )
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

    image_description = chain.run(description)

    image_url = DallEAPIWrapper(model="dall-e-3").run(image_description)

    if image_url:
        urllib.request.urlretrieve(image_url, "image.jpg")
        return "image.jpg"
    else:
        return None
