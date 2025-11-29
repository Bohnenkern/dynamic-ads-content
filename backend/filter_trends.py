"""
prepare_chat_prompt.py

Read a JSON file and output a single ChatGPT prompt containing the file's contents.

Usage:
    python prepare_chat_prompt.py path/to/file.json --output prompt.txt --instruction "Summarize this data"

This script prints the prepared prompt to stdout by default or writes to a file if `--output` is passed.
It also includes a simple token-size estimation and will warn if the prompt is likely to exceed common model limits.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Optional
from dotenv import load_dotenv
import importlib


def read_json_file(path: str) -> Any:
    """Load a JSON file and return the parsed object.

    Raises FileNotFoundError or json.JSONDecodeError on error.
    """
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def build_prompt(data: Any, instruction: Optional[str] = None, pretty: bool = True, wrap: bool = True) -> str:
    """Construct a prompt string for ChatGPT that includes the JSON data.

    - instruction: short instruction for the assistant, default is a neutral request
    - pretty: if True will pretty-print the JSON
    - wrap: if True encase the JSON in ```json``` code block markers
    """
    # Default instruction: neutral summary
    default_instruction = (
        "From the following trending topics, find those which are suitable to be merged into general marketing campaigns. "
        "The connection may be broad. Hard constraints include (but are not limited to): topics that are negative, political, religious, racist, sexist, illegal, associated with certain people, drugs or weapons are NOT suitable. "
        "Return the results in the same JSON form, but delete the unsuitable entries."
    )

    instruction = instruction or default_instruction

    if pretty:
        json_text = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        json_text = json.dumps(data, separators=(',', ':'), ensure_ascii=False)

    # Avoid using Markdown code fences (```json ... ```) so the assistant returns a plain JSON object
    # Instead we include the raw JSON text in the prompt. This prevents models from attaching fences
    # or extra text and helps ensure they return valid JSON when asked.
    if wrap:
        body = json_text
    else:
        body = json_text

    prompt = f"{instruction}\n\n{body}\n"
    return prompt


def estimate_tokens_from_string(s: str) -> int:
    """Approximate token count from characters.

    This is a rough heuristic: tokens ≈ characters / 4
    Different models and languages may vary; adjust if needed.
    """
    return math.ceil(len(s) / 4)


def filter_data_with_openai(
    data: Any,
    instruction: Optional[str] = None,
    model: str = 'gpt-4o-mini',
    temperature: float = 0.0,
    api_key: Optional[str] = None,
    api_output: Optional[str] = None,
) -> Any:
    """Builds the prompt from data and calls the OpenAI Chat API, returning parsed JSON or raw text.

    If `api_key` is not provided, the function tries to read `OPENAI_API_KEY` from environment.
    Returns: parsed JSON (dict/list) if the model returns valid JSON, otherwise returns raw string.
    """
    prompt = build_prompt(data, instruction=instruction, pretty=True, wrap=True)

    # Load env .env and fallback to environment variable
    load_dotenv()
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not provided; pass api_key or set environment variable.')

    try:
        openai_mod = importlib.import_module('openai')
    except Exception as e:
        raise RuntimeError('openai package not installed') from e

    # Use new OpenAI client if available
    if hasattr(openai_mod, 'OpenAI'):
        client = openai_mod.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        content = response.choices[0].message.content
    elif hasattr(openai_mod, 'ChatCompletion'):
        openai_mod.api_key = api_key
        legacy_resp = openai_mod.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        content = legacy_resp['choices'][0]['message']['content']
    else:
        raise RuntimeError('Installed openai package does not expose a usable chat API')

    # Try parse JSON
    try:
        parsed = json.loads(content)
        if api_output:
            with open(api_output, 'w', encoding='utf-8') as fh:
                json.dump(parsed, fh, indent=2, ensure_ascii=False)
        return parsed
    except Exception:
        # Not JSON, write raw string if requested
        if api_output:
            with open(api_output, 'w', encoding='utf-8') as fh:
                fh.write(content)
        return content


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Create a single ChatGPT prompt from a JSON file")
    parser.add_argument('json_file', nargs='?', default='trends.json', help='Path to the JSON file (defaults to trends.json)')
    parser.add_argument('--output', '-o', default=None, help='Write prompt to this file instead of printing')
    parser.add_argument('--instruction', '-i', default=None, help='Instruction text for ChatGPT (optional)')
    parser.add_argument('--filter-trends', dest='filter_trends', action='store_true', help='Use the built-in filter-for-marketing instruction (recommended for trends.json)')
    parser.add_argument('--pretty', action='store_true', default=True, help='Pretty-print JSON inside the prompt')
    parser.add_argument('--no-wrap', dest='wrap', action='store_false', help='Do not wrap JSON inside a ```json``` block')
    parser.add_argument('--max-tokens-warn', type=int, default=3800, help='Warn if estimated tokens exceed this number')
    parser.add_argument('--call-api', dest='call_api', action='store_true', help='Send the prepared prompt to OpenAI ChatGPT API')
    parser.add_argument('--no-call-api', dest='no_call_api', action='store_true', help="Don't call the OpenAI API (useful if you want to just create prompt)")
    parser.add_argument('--model', dest='model', default='gpt-4o-mini', help='Model name to call (e.g., gpt-4o-mini, gpt-4o)')
    parser.add_argument('--temperature', type=float, default=0.0, help='Temperature for the model')
    parser.add_argument('--api-output', dest='api_output', default=None, help='Write the API reply to this file')
    args = parser.parse_args(argv)

    # Validation: file exists
    if not os.path.exists(args.json_file):
        print(f"Error: JSON file not found: {args.json_file}", file=sys.stderr)
        return 2

    try:
        data = read_json_file(args.json_file)
    except Exception as e:
        print(f"Error reading/parsing JSON file: {e}", file=sys.stderr)
        return 3

    # If the default file is expected but not found, this will already have returned.

    # Use the filter-trends preset if the user requested it or the JSON filename suggests trends data
    use_filter_preset = args.filter_trends or os.path.basename(args.json_file).lower() == 'trends.json'
    if use_filter_preset and not args.instruction:
        # Pass the instruction preset to the builder by setting args.instruction to the preset text
        args.instruction = (
            "From the following trending topics, find those which are suitable to be merged into general marketing campaigns. "
            "The connection may be broad. Hard constraints are for example, but not limited to: topics that are negative, political, religious, racist, sexist, illegal, associated with certain people, drugs or weapons. "
            "Return them in the same form, just delete the unsuitable ones."
        )

    prompt = build_prompt(data, instruction=args.instruction, pretty=args.pretty, wrap=args.wrap)

    estimated_tokens = estimate_tokens_from_string(prompt)
    if estimated_tokens >= args.max_tokens_warn:
        print(
            f"⚠️  Warning: Estimated prompt tokens {estimated_tokens} >= {args.max_tokens_warn}. "
            f"This may exceed the context window of some models. Consider summarizing or chunking the input.",
            file=sys.stderr,
        )

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as fh:
                fh.write(prompt)
            print(f"Prompt written to: {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 4
    else:
        # Print to stdout
        print(prompt)
    # Continue to API call logic after writing/printing prompt
    # If requested, call the OpenAI API with the prepared prompt
    # Default behavior: load .env first, then call the API if OPENAI_API_KEY is present unless --no-call-api is passed.
    load_dotenv()  # pick up environment variables from .env if present
    env_has_key = os.getenv('OPENAI_API_KEY') is not None
    call_api = args.call_api or (not args.no_call_api and env_has_key)
    if call_api:
        load_dotenv()  # pick up environment variables from .env if present
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not set (or not present in .env).", file=sys.stderr)
            return 5

        # Configure the OpenAI client
        try:
            import openai
        except Exception:
            print("Error: openai python package not installed. Install it or run with --no-call-api.", file=sys.stderr)
            return 6
        openai.api_key = api_key

        try:
            print(f"Calling OpenAI model {args.model} ...")
            # Dynamically inspect the openai package and choose the right interface
            try:
                import importlib
                openai_mod = importlib.import_module('openai')
            except Exception:
                print("Error: openai python package not installed. Install it or run with --no-call-api.", file=sys.stderr)
                return 6

            # New interface (openai>=1.0.0) exposes OpenAI class
            if hasattr(openai_mod, 'OpenAI'):
                client = openai_mod.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=args.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=args.temperature,
                    max_tokens=2000,
                )
                content = response.choices[0].message.content
            # Legacy interface uses ChatCompletion
            elif hasattr(openai_mod, 'ChatCompletion'):
                openai_mod.api_key = api_key
                legacy_resp = openai_mod.ChatCompletion.create(
                    model=args.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=args.temperature,
                    max_tokens=2000,
                )
                content = legacy_resp['choices'][0]['message']['content']
            else:
                print("Error: Installed openai package does not expose a usable Chat API (OpenAI or ChatCompletion).", file=sys.stderr)
                return 6
        except Exception as e:
            print(f"Error calling OpenAI: {e}", file=sys.stderr)
            return 6

        if not args.api_output:
            args.api_output = 'filtered_trends.json'
        if args.api_output:
            try:
                # Try to parse the response as JSON and pretty-print it
                try:
                    parsed = json.loads(content)
                    with open(args.api_output, 'w', encoding='utf-8') as fh:
                        json.dump(parsed, fh, indent=2, ensure_ascii=False)
                except Exception:
                    # Fallback: write raw text (not JSON)
                    with open(args.api_output, 'w', encoding='utf-8') as fh:
                        fh.write(content)
                print(f"API reply written to: {args.api_output}")
            except Exception as e:
                print(f"Error writing API output: {e}", file=sys.stderr)
                return 7
        else:
            print("\n=== OpenAI response ===\n")
            print(content)
            print("\n=== End response ===\n")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
