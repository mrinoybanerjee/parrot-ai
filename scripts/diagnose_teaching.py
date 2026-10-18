"""Local-only diagnostic: preserve raw summaries for manual six-case grading."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
from types import SimpleNamespace
from unittest.mock import MagicMock
from urllib.request import ProxyHandler, Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from openai import OpenAI
from backend.src.chatbot import DualChatbot

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:11434'
MODEL = 'qwen3:4b'
CAREFUL_SYSTEM = (
    'You are an English usage reviewer, not an error-finding exercise. '
    'Give brief learning notes grounded in exact quoted phrases from the transcript. '
    'Preserve valid wording. Separate required grammatical corrections from optional '
    'register choices and meaning differences. Explain context dependence or uncertainty '
    'instead of guessing. Do not invent errors or rules. If a phrase is already valid, say so.'
)


def messages_for(case):
    roles = {'role1': {'name': 'Customer', 'action': 'ordering food'},
             'role2': {'name': 'Waitstaff', 'action': 'taking the order'}}
    bot = DualChatbot('OpenAI', roles, 'English', case['scenario'],
                      'Beginner', 'Conversation', 'Short', URL)
    bot.conversation_history = [{'bot': 'Customer' if i % 2 == 0 else 'Waitstaff', 'text': text}
                                for i, text in enumerate(case['utterances'])]
    speaker = bot.chatbots['role1']['chatbot']
    speaker.memory = [{'role': 'Customer', 'text': text}
                      for i, text in enumerate(case['utterances']) if i % 2 == 0]
    captured = {}

    def capture(**kwargs):
        captured.update(deepcopy(kwargs))
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='captured'))])

    for item in bot.chatbots.values():
        item['chatbot'].client.close()
    speaker.client = MagicMock()
    speaker.client.chat.completions.create.side_effect = capture
    bot.summary()
    return captured['messages']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--production-repro', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new output path; existing diagnostic evidence is not overwritten.')
    source = ROOT / 'data/teaching-diagnostic-v1.json'
    cases = json.loads(source.read_text())['cases']
    # No alternate hosts, model pulls or environment proxies are used.
    with build_opener(ProxyHandler({})).open(URL + '/api/tags', timeout=10) as response:
        installed = json.load(response)['models']
    selected = next((item for item in installed if item['name'] == MODEL), None)
    if selected is None:
        parser.error('Required local qwen3:4b is not installed; no model will be downloaded.')
    with build_opener(ProxyHandler({})).open(URL + '/api/version', timeout=10) as response:
        server_version = json.load(response)['version']
    result = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'model': selected,
              'python': platform.python_version(), 'os': platform.platform(),
              'ollama_version': server_version,
              'fixture_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'controls': None if args.production_repro else {
                  'api': '/api/chat', 'seed': 53, 'temperature': 0,
                  'num_predict': 1200, 'think': False},
              'limitations': (
                  'One replay using production SDK defaults; no decoding overrides. '
                  'Fixed synthetic English transcript, not a teaching-quality benchmark.'
                  if args.production_repro else
                  'Fixed small English diagnostic, manual rubric. Controlled decoding '
                  'and native Ollama transport differ from production defaults; '
                  'scenarios/ground truth are not sent to the summary model. No quality percentage.'),
              'outputs': []}
    client = OpenAI(base_url=URL + '/v1', api_key='sk-no-key-required', timeout=120,
                    max_retries=0, http_client=httpx.Client(trust_env=False))
    conditions = (['production-defaults'] if args.production_repro else
                  ['current-history', 'transcript-only', 'careful-transcript'])
    for condition in conditions:
        for case in cases[:1] if args.production_repro else cases:
            messages = messages_for(case)
            if condition in ('transcript-only', 'careful-transcript'):
                messages = [messages[0], messages[-1]]
            if condition == 'careful-transcript':
                messages[0]['content'] = CAREFUL_SYSTEM
            start = time.perf_counter()
            row = {'condition': condition, 'case': case['id'], 'messages': messages}
            try:
                if args.production_repro:
                    response = client.chat.completions.create(model=MODEL, messages=messages)
                    raw = response.model_dump()
                    answer = response.choices[0].message.content
                    finish = response.choices[0].finish_reason
                else:
                    payload = dict(model=MODEL, messages=messages, stream=False, think=False,
                                   options=dict(seed=53, temperature=0, num_predict=1200))
                    request = Request(URL + '/api/chat', data=json.dumps(payload).encode(),
                                      headers={'Content-Type': 'application/json'})
                    with build_opener(ProxyHandler({})).open(request, timeout=120) as response:
                        raw = json.load(response)
                    answer = raw['message']['content']
                    finish = raw.get('done_reason')
                row.update(response=raw, answer=answer, finish_reason=finish,
                           elapsed_seconds=time.perf_counter() - start)
            except Exception as error:
                row.update(error=type(error).__name__, elapsed_seconds=time.perf_counter() - start)
            result['outputs'].append(row)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + '\n')
            print(condition, case['id'], row.get('finish_reason', row.get('error')), flush=True)
    client.close()


if __name__ == '__main__':
    main()
