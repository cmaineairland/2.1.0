import json
import importlib
from openai import OpenAI
from openai import OpenAIError


class LLMResponseFetcher:
    def __init__(self):
        try:
            # 明确指定UTF-8编码
            with open('config.json', encoding='utf-8') as f:
                config = json.load(f)
            self.API_SECRET_KEY = config.get('LLMsApiKey')
            self.BASE_URL = config.get('LLMsUrl')
            self.MODEL = config.get('LLMsModel')

            if not all([self.API_SECRET_KEY, self.BASE_URL, self.MODEL]):
                raise ValueError("Missing required configuration in config.json")

            # 明确指定UTF-8编码
            with open('functionCall.json', encoding='utf-8') as f:
                self.functions = json.load(f)
        except FileNotFoundError:
            print("Error: config.json or functionCall.json file not found.")
        except json.JSONDecodeError:
            print("Error: Failed to parse config.json or functionCall.json.")
        except ValueError as e:
            print(f"Error: {e}")

    def _create_client(self):
        return OpenAI(api_key=self.API_SECRET_KEY, base_url=self.BASE_URL)

    def getResponse(self, prompt):
        client = self._create_client()
        try:
            resp = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                functions=self.functions,
                function_call="auto"
            )
            return self._handle_function_call(resp)
        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
            return None

    def getStreamResponse(self, prompt):
        client = self._create_client()
        try:
            stream = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                functions=self.functions,
                function_call="auto",
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.function_call:
                    yield self._handle_function_call(chunk)
                else:
                    yield chunk
        except OpenAIError as e:
            print(f"OpenAI API error: {e}")

    def get(self, prompt, stream=False):
        if stream:
            return self.getStreamResponse(prompt)
        else:
            return self.getResponse(prompt)

    def _handle_function_call(self, response):
        choice = response.choices[0]
        if choice.message.function_call:
            function_name = choice.message.function_call.name
            parameters = choice.message.function_call.parameters
            try:
                module = importlib.import_module(f'function.{function_name}.{function_name}')
                function = getattr(module, function_name)
                result = function(**parameters)
                return result
            except ImportError:
                print(f"Error: Function module {function_name}.py not found.")
            except AttributeError:
                print(f"Error: Function {function_name} not found in {function_name}.py.")
            except Exception as e:
                print(f"Error: Failed to execute function {function_name}: {e}")
        return response


if __name__ == "__main__":
    user_prompt = "请搜索人工智能的相关链接"
    DS = LLMResponseFetcher()
    resp = DS.get(user_prompt)
    print(resp)
