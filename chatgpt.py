import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
CHECK_LISTS = int(os.getenv("CHECK_LISTS_NUM"))
ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_task_for_ai(data: dict) -> str:
    """
        Generates a task for the AI based on the provided data.

        Args:
            data (dict): A dictionary containing the data for the task.

        Returns:
            str: The generated task as a string.
        """
    task = "Analyze the photo and the report. Describe what is wrong with the cleanliness at the location:"
    task += f"Location: {data['chosen_location']}\n"
    for i in range(0, CHECK_LISTS):
        if f"comment_entry_{i + 1}" in data:
            task += f"Check list {i + 1} A comment: {data[f'comment_entry_{i + 1}']}\n"
        else:
            task += f"Check list {i + 1} all clear \n"

    return task


async def analyze_task(report: str, photos: dict) -> str | None:
    """
        Analyzes the task using the AI and returns the result.

        Args:
            report (str): The report to analyze.
            photos (dict): A dictionary containing the photos to analyze.

        Returns:
            str | None: The analysis result as a string, or None if an error occurs.
        """
    try:
        message_request = [{"type": "text", "text": report}]

        for url in photos.values():
            message_request.append(
                {"type": "image_url", "image_url": {"url": url}}
            )

        response = ai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user", "content": message_request}],
            max_tokens=1000,
        )
        return (
            response.choices[0].message.content if response.choices else None
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
