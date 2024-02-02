# Telegram Bot with OpenAI Integration

This project involves developing a Telegram bot in the Python programming language using the aiogram library and
integrating with OpenAI.

The bot's functionality allows users to choose a specific number of available locations and fill out a checklist, which
includes uploading photos and adding comments. After completing the checklist, the bot leverages the capabilities of OpenAI to analyze and process the gathered information, resulting in the creation of a detailed report. This report is automatically sent to the user, enabling them to receive structured information about their choices and interactions with the bot.

## Features 
- Checklist Completion: Users can fill out checklists, including uploading photos and comments.

- OpenAI Integration: The bot integrates with OpenAI to analyze and process the collected data.

- Detailed Reports: The application automatically generates detailed reports based on the analyzed information.

- Automatic Report Delivery: Reports are automatically sent to the user, streamlining the communication process.

- Structured Information: Users receive structured information regarding their choices and interactions with the bot.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Telegram API Token
- OpenAI API Token

### Installation

Для запуску проекту виконайте наступні кроки:

1. Clone the repository:

```bash
https://github.com/Daniil-Pankieiev/The_Best_Telegram_Bot.git
```
2. Create and activate the virtual environment:

On macOS and Linux:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
On Windows:
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```
3. Install the necessary dependencies:

```bash
pip install -r requirements.txt
```

4. Copy .env.sample to .env and populate it with all required data.

5. Run the bot:

On macOS and Linux:
```bash
python3 main.py
```

On Windows:
```bash
python main.py
```
## Contributing
Feel free to contribute to these enhancements, and let's make our Telegram Bot even better!
## Conclusion

Thank you for using the Telegram Bot! 
