import streamlit as st
import json
import openai
from pydantic import BaseModel, Field
import io
import os
from PIL import Image
from stability_sdk import client as stability_client


class Ingredient(BaseModel):
    ingredient: str = Field(discription="材料", examples=["鶏もも肉"])
    quantity: str = Field(discription="分量", examples=["300g"])


class Recipe(BaseModel):
    ingredients: list[Ingredient]
    instructions: list[str] = Field(discription="手順", examples=[
                                    ["材料を切ります。", "材料を炒めます。"]])
    in_english: str = Field(discription="料理名の英語")


OUTPUT_RECIPE_FUNCTION = {
    "name": "output_recipe",
    "description": "レシピを出力する",
    "parameters": Recipe.schema(),
}

PROMPT_TEMPLATE = """料理のレシピを考えてください。


料理名: {dish}

"""

st.title("レシピ生成AI")
dish = st.text_input(label="料理名")

if dish:
    with st.spinner(text="生成中..."):
        messages = [
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(dish=dish)
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=[OUTPUT_RECIPE_FUNCTION],
            function_call={"name": OUTPUT_RECIPE_FUNCTION["name"]},
        )
        response_message = response["choices"][0]["message"]
        function_call_args = response_message["function_call"]["arguments"]

        recipe = json.loads(function_call_args)

        st.write("## 材料")
        st.table(recipe["ingredients"])

        instruction_markdown = "## 手順\n"
        for i, instruction in enumerate(recipe["instructions"]):
            instruction_markdown += f"{i+1}. {instruction}\n"

        st.write(instruction_markdown)

        # 画像生成
        stability_api = stability_client.StabilityInference(
            key=os.environ["STABILITY_KEY"], engine="stable-diffusion-xl-1024-v1-0"
        )

        answers = stability_api.generate(
            prompt=recipe["in_english"], height=512, width=512, samples=1
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == stability_client.generation.FILTER:
                    st.warning("画像を生成できませんでした")
                if artifact.type == stability_client.generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    st.image(img)
