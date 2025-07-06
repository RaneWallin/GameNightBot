# commands/ask_ai.py

import os
from openai import OpenAI
from discord import Interaction
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_ask_ai(interaction: Interaction, question: str):
    await interaction.response.defer()

    prompt = f"You are a mideval squire with a penchant for board games and their rules. Please answer the following question clearly, concisely and accurately:\n\n{question}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()

        await interaction.followup.send(
            f"⚠️ *This response is AI generated and may be inaccurate or completely wrong. Use your judgment and refer to the official rules when in doubt.*\n\n"
            f"**Question:** {question}\n\n**Answer:** {answer}"
        )

    except Exception as e:
        await interaction.followup.send(
            f"❌ Failed to get an answer from the AI: {str(e)}"
        )
