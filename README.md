# FLEM - Fix Last Executed Mistake

FLEM is a command-line tool that helps fix bash commands. It retrieves the last executed bash command from your history, sends it to GPT for correction, and then allows you to execute the corrected command.
 
## Features

* Ultra simple
* No external dependencies

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/flem.git
   cd flem
   ```
 
2. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

Run the script with:
``` sh
python flem.py [options]
```
Options:
- `-v`, `--verbose`: Enable verbose output
- `-h`, `--help`: Show the help message and exit

## Safety Features

- The script checks for potentially dangerous commands (e.g., `rm`, `dd`, `mkfs`) and asks for confirmation before executing them.
- The OpenAI API call is configured with a low temperature setting to reduce randomness in the output.
